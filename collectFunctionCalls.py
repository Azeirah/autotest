#!/usr/bin/python3

"""
Given a parsed PHP trace (PHPTraceParser.py@Trace)
This file will parse all function calls, with their parameters and their respective return values.
"""

import argparse
import sqlite3
import os
import os.path
import re
import time
import sys
import traceback
import datetime
import uuid
from contextlib import contextmanager
from timeit import default_timer
from collections import Counter
from pprint import pprint

import PHPTraceParser
import PHPTraceTokenizer
import PHPProfileParser
from settings import traceDir

@contextmanager
def elapsed_timer():
    """https://stackoverflow.com/a/30024601"""
    start = default_timer()
    elapser = lambda: default_timer() - start
    yield lambda: elapser()
    end = default_timer()
    elapser = lambda: end-start

parser = argparse.ArgumentParser(description="Add function-call-parameters to a database")
parser.add_argument('request', nargs="?", type=str, help="trace request")
parser.add_argument('-d', '--db', nargs="?", dest="db", type=str, default="function-calls.db", help="name of the sqlite3 .db file")
parser.add_argument('-a', '--auto-import', action="store_true", dest="autoImport", default=False, help="Automatically import all unprocessed traces")
parser.add_argument('-r', '--auto-remove', action="store_true", dest="autoRemove", default=False, help="Remove traces after succesfully processing")

os.chdir(os.path.split(__file__)[0])
schema_path = "schema.sql"

def open_db_connection(db_name):
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA synchronous = OFF")
    return conn

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

    fmt = re.compile(r"(?P<seconds>\d+)_(?P<microseconds>\d+) (?P<uid>[a-zA-Z0-9@\-]+)(?P<ext>\.x[pt])")

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
    with open_db_connection(db_name) as conn:
        c = conn.cursor()
        with open(schema_path) as f:
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

    params = [
        {
            'value_id': value_ids[idx],
            'function_invocation_id': function_invocation_id
        }

        for idx, parameter in enumerate(parameters)
    ]

    c = conn.cursor()
    c.executemany("""
        INSERT INTO `invocation_parameters` VALUES (:function_invocation_id, :value_id)
    """, params)

def insert_request(request, conn):
    c = conn.cursor()
    timestamp = datetime.datetime.today().isoformat()
    c.execute("INSERT INTO `traces` (`requestname`, `timestamp`) VALUES (:requestname, :timestamp);", {'requestname': request, 'timestamp': timestamp})
    conn.commit()

def insert_trace(trace, conn):
    with elapsed_timer() as traceParseTimer:
        calls = PHPTraceParser.ordered_function_calls(trace)
    print("Took {:.4f}s to parse traces".format(traceParseTimer()))

    values = set()
    file_names = set()
    function_names = set()
    function_invocations = []
    params = []
    for call in calls:
        name = call['name']
        h = str(uuid.uuid4())
        retval = call['return']
        definition_filename = call['definition_filename']
        calling_filename = call['calling_filename']

        for param in call['parameters']:
            values.add((param,))
            params.append({
                "function_invocation_hash": h,
                "value": param
            })

        values.add((retval,))

        file_names.add((definition_filename,))
        file_names.add((calling_filename,))

        function_names.add((name,))

        function_invocations.append({
            "name": name,
            "returnval": retval,
            "calling_filename": calling_filename,
            "definition_filename": definition_filename,
            "linenum": call['line_number'],
            "hash": h
        })

    c = conn.cursor()
    c.execute("BEGIN TRANSACTION")

    with elapsed_timer() as db_timer:
        c.executemany(
            """INSERT OR IGNORE INTO `values` VALUES (:value)""",
            values
        )

        prev_time = 0
        new_time = db_timer()
        print("Took {:.4f}s to insert {} `values`".format(new_time - prev_time, len(values)))
        prev_time = new_time

        c.executemany(
            """INSERT OR IGNORE into `file_names` VALUES (:file_name)""",
            file_names
        )
        new_time = db_timer()
        print("Took {:.4f}s to insert {} `file_names`".format(new_time - prev_time, len(file_names)))
        prev_time = new_time

        c.executemany(
            """INSERT OR IGNORE into `function_names` VALUES (:function_name)""",
            function_names
        )
        new_time = db_timer()
        print("Took {:.4f}s to insert {} `function_names`".format(new_time - prev_time, len(function_names)))
        prev_time = new_time

        c.executemany(
            """
            INSERT INTO
                `function_invocations`
                (
                 `name`,
                 `returnval`,
                 `calling_filename`,
                 `definition_filename`,
                 `linenum`,
                 `hash`
                )
            VALUES
                (
                 (SELECT `rowid` FROM `function_names` WHERE `name`=:name),
                 (SELECT `rowid` FROM `values` WHERE `value`=:returnval),
                 (SELECT `rowid` FROM `file_names` WHERE `name`=:calling_filename),
                 (SELECT `rowid` FROM `file_names` WHERE `name`=:definition_filename),
                 :linenum,
                 :hash
                );
            """,
            function_invocations
        )
        new_time = db_timer()
        print("Took {:.4f}s to insert {} `function_invocations`".format(new_time - prev_time, len(function_invocations)))
        prev_time = new_time

        c.executemany(
            """
            INSERT INTO `invocation_parameters` VALUES
            (
                :function_invocation_hash,
                (SELECT `rowid` FROM `values` WHERE `value`=:value)
            )
            """,
            params)
        new_time = db_timer()
        print("Took {:.4f}s to insert {} `invocation_parameters`".format(new_time - prev_time, len(params)))
        prev_time = new_time

        # c.execute("COMMIT")
        conn.commit()
        new_time = db_timer()
        print("Took {:.4f}s to commit to db".format(new_time - prev_time))
        prev_time = new_time

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
    request = requests[uid]

    profiles = request['profile']
    traces = request['trace']

    if not request_exists(uid, conn):
        profile_filenames = [os.path.join(traceDir, profile['filename']) for profile in profiles]

        with elapsed_timer() as profiler_timer:
            function_mappings = PHPProfileParser.get_function_file_mapping(profile_filenames)
        print("Took {:.4f} seconds to parse profile".format(profiler_timer()))

        for trace in traces:
            with elapsed_timer() as trace_timer:
                trace = create_trace(trace['path'], function_mappings)
            print("Took {:.4f} seconds to tokenize trace".format(trace_timer()))

            insert_trace(trace, conn)
            insert_request(uid, conn)

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
        with open_db_connection(db_name) as conn:
            insert_request_in_db(conn, args.request, args.autoRemove)

    if args.autoImport:
        requests = get_unique_requests_from_folder(traceDir)

        for uid in requests:
            print("Found request --{}--".format(uid))
            with open_db_connection(db_name) as conn:
                try:
                    insert_request_in_db(conn, requests, uid, args.autoRemove)
                except Exception as e:
                    print("Error while processing, moving on to the next")
                    traceback.print_exc()
            print("Done processing request --{}--\n".format(uid))
