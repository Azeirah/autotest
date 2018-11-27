#!/usr/bin/python3

"""
Given a parsed PHP trace (PHPTraceParser.py@Trace)
This file will parse all function calls, with their parameters and their respective return values.
"""

import argparse
import sqlite3
import os.path
import re
import time
import sys
import traceback
import datetime
from collections import Counter
from pprint import pprint

import PHPTraceParser
import PHPTraceTokenizer
import PHPProfileParser
from settings import traceDir

parser = argparse.ArgumentParser(description="Add function-call-parameters to a database")
parser.add_argument('request', nargs="?", type=str, help="trace request")
parser.add_argument('-d', '--db', nargs="?", dest="db", type=str, default="function-calls.db", help="name of the sqlite3 .db file")
parser.add_argument('-a', '--auto-import', action="store_true", dest="autoImport", default=False, help="Automatically import all unprocessed traces")
parser.add_argument('-r', '--auto-remove', action="store_true", dest="autoRemove", default=False, help="Remove traces after succesfully processing")

def parse_request_filename(filename):
    """Takes a filename of a file in the traces directory
    and returns the timestamp, whether it's a profile or trace file,
    and a unique id for that specific request.

    Returns False on failure"""

    info = {
        'type': None,
        'timestamp': None,
        'request_id': None,
        'filename': filename
    }

    fmt = re.compile(r"(?P<seconds>\d+)_(?P<microseconds>\d+) (?P<uid>[a-zA-Z0-9\-]+)(?P<ext>\.x[pt])")

    match = fmt.match(filename)

    if match:
        ext = match.group('ext')

        if '.xp' in ext:
            info['type'] = 'profile'
        elif '.xt' in ext:
            info['type'] = 'trace'
        else:
            return False

        t = float(match.group('seconds') + '.' + match.group('microseconds'))
        info['timestamp'] = datetime.datetime.fromtimestamp(t)

        info['request_id'] = match.group('uid')

        return info

    return False

def set_up_db(db_name):
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        with open('schema.sql') as f:
            c.executescript(f.read())
        conn.commit()

def request_exists(request, conn):
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM `traces` WHERE `requestname`=?", (request,))
    return c.fetchone()[0] >= 1

def insert_parameters(parameters, function_invocation_id, conn):
    value_ids = []

    for parameter in parameters:
        value_ids.append(insert_value(parameter, conn))

    for idx, parameter in enumerate(parameters):
        insert_parameter(value_ids[idx], function_invocation_id, conn)

def insert_parameter(value_id, function_invocation_id, conn):
    c = conn.cursor()

    args = {
        'value_id': value_id,
        'function_invocation_id': function_invocation_id
    }

    c.execute("""
        INSERT INTO `invocation_parameters` VALUES (:function_invocation_id, :value_id)
    """, args)

    return c.lastrowid

def insert_value(value, conn):
    c = conn.cursor()

    args = {
        'value': value
    }

    c.execute("SELECT `rowid` FROM `values` WHERE `value`=:value", args)
    rowid = c.fetchone()

    try:
        return rowid[0]
    except TypeError:
        c.execute("""
            INSERT INTO `values` VALUES (:value)
        """, args)
        return c.lastrowid


def insert_request(request, conn):
    c = conn.cursor()
    timestamp = datetime.datetime.today().isoformat()
    c.execute("INSERT INTO `traces` (`requestname`, `timestamp`) VALUES (:requestname, :timestamp);", {'requestname': request, 'timestamp': timestamp})
    conn.commit()

def insert_filename(filename, conn):
    c = conn.cursor()

    args = {
        'filename': filename
    }

    c.execute("""
        SELECT `rowid` FROM `file_names` WHERE name=:filename
    """, args)

    rowid = c.fetchone()

    try:
        return rowid[0]
    except TypeError:
        c.execute("""
            INSERT INTO `file_names` VALUES (:filename)
        """, args)

        return c.lastrowid

def insert_function_name(function_name, conn):
    c = conn.cursor()

    args = {
        'function_name': function_name
    }

    c.execute("""
        SELECT `rowid` FROM `function_names` WHERE name=:function_name
    """, args)

    rowid = c.fetchone()

    try:
        return rowid[0]
    except TypeError:
        c.execute("""
            INSERT INTO `function_names` VALUES (:function_name)
        """, args)

        return c.lastrowid

def insert_trace(trace, conn):
    c = conn.cursor()
    calls = PHPTraceParser.grouped_function_calls(trace)

    for name, calls in calls.items():
        for call in calls:
            retval = call.get('return', '{{void}}')

            definition_filename_id = insert_filename(call['definition_filename'], conn)
            calling_filename_id = insert_filename(call['calling_filename'], conn)
            function_id = insert_function_name(name, conn)
            returnval_id = insert_value(retval, conn)

            c.execute("""
                INSERT INTO
                    `function_invocations`
                    (`name`, `returnval`, `calling_filename`, `definition_filename`, `linenum`)
                VALUES
                    (:name, :returnval, :calling_filename, :definition_filename, :linenum)

                """,
                {
                    'name': function_id,
                    'returnval': returnval_id,
                    'calling_filename': calling_filename_id,
                    'definition_filename': definition_filename_id,
                    'linenum': call['line_number']
                }
            )
            function_invocation_id = c.lastrowid

            insert_parameters(call['parameters'], function_invocation_id, conn)

    conn.commit()

def trace_and_profile_from_request(traceDir, request):
    return (
        os.path.join(traceDir, "{}.xt".format(request)),
        os.path.join(traceDir, "{}.xp".format(request))
    )

def create_trace(traceFile, function_mappings):
    return PHPTraceTokenizer.Trace(traceFile, function_mappings)

def remove_request_files(request):
    for trace in request['trace']:
        try:
            os.unlink(trace['path'])
        except PermissionError:
            # httpd process often locks the file
            # doesn't matter if it can't be cleaned now
            # will be cleaned on next removal run
            pass
    for trace in request['profile']:
        try:
            os.unlink(trace['path'])
        except PermissionError:
            # httpd process often locks the file
            # doesn't matter if it can't be cleaned now
            # will be cleaned on next removal run
            pass

def insert_request_in_db(conn, requests, uid, autoRemove=False):
    start_time = time.time()

    request = requests[uid]

    profiles = request['profile']
    traces = request['trace']

    if not request_exists(uid, conn):
        profile_filenames = [os.path.join(traceDir, profile['filename']) for profile in profiles]
        function_mappings = PHPProfileParser.get_function_file_mapping(profile_filenames)

        for trace in traces:
            trace = create_trace(trace['path'], function_mappings)
            insert_trace(trace, conn)
            insert_request(uid, conn)
            elapsed_time = time.time() - start_time
            print("Took {:.0f} seconds to process request --{}--".format(elapsed_time, uid))
        if autoRemove:
            remove_request_files(request)
    else:
        print("This request has already been processed!")
        if autoRemove:
            remove_request_files(request)

def get_unique_requests_from_folder(traceDir):
    """id > profile/trace > []"""
    requestFiles = [parse_request_filename(tp) for tp in os.listdir(traceDir)]
    requestFiles = [file for file in requestFiles if file]

    requests = {}

    for request in requestFiles:
        request["path"] = os.path.join(traceDir, request['filename'])
        if request["request_id"] not in requests:
            requests[request["request_id"]] = {}

        if request["type"] in requests[request["request_id"]]:
            requests[request["request_id"]][request["type"]].append(request)
        else:
            requests[request["request_id"]][request["type"]] = [request]

    return requests

if __name__ == '__main__':
    args = parser.parse_args()
    db_name = args.db

    if not os.path.exists(db_name):
        set_up_db(db_name)

    if args.request:
        with sqlite3.connect(db_name) as conn:
            insert_request_in_db(conn, args.request, args.autoRemove)

    if args.autoImport:
        requests = get_unique_requests_from_folder(traceDir)

        for uid in requests:
            print("Found request --{}--".format(uid))
            with sqlite3.connect(db_name) as conn:
                try:
                    insert_request_in_db(conn, requests, uid, args.autoRemove)
                except Exception as e:
                    print("Error while processing, moving on to the next")
                    traceback.print_exc()
            print("Done processing request --{}--\n".format(uid))

        # for request, count in Counter(files).items():
        #     if count == 2 and re.match(r"^\d+", request):
        #         print("Found request --{}--".format(request))
        #         with sqlite3.connect(db_name) as conn:
        #             try:
        #                 insert_request_in_db(conn, request, args.autoRemove)
        #             except Exception as e:
        #                 print("Error while processing, moving on to the next")
        #                 traceback.print_exc()
        #         print("Done processing request --{}--\n".format(request))
            # else:
            #     print("Invalid request:", request)
