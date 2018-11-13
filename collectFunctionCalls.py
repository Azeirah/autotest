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
from collections import Counter

import PHPTraceParser
import PHPTraceTokenizer
import PHPProfileParser
from settings import traceDir

parser = argparse.ArgumentParser(description="Add function-call-parameters to a database")
parser.add_argument('timestamp', nargs="?", type=str, help="trace timestamp")
parser.add_argument('-d', '--db', nargs="?", dest="db", type=str, default="function-calls.db", help="name of the sqlite3 .db file")
parser.add_argument('-a', '--auto-import', action="store_true", dest="autoImport", default=False, help="Automatically import all unprocessed traces")
parser.add_argument('-r', '--auto-remove', action="store_true", dest="autoRemove", default=False, help="Remove traces after succesfully processing")

def set_up_db(db_name):
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        with open('schema.sql') as f:
            c.executescript(f.read())
        conn.commit()

def timestamp_exists(timestamp, conn):
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM `traces` WHERE `timestamp`=?", (timestamp,))
    return c.fetchone()[0] >= 1

def insert_timestamp(timestamp, conn):
    c = conn.cursor()
    c.execute("INSERT INTO `traces` VALUES (?);", (timestamp,))
    conn.commit()

def insert_trace(trace, conn):
    c = conn.cursor()
    calls = PHPTraceParser.grouped_function_calls(trace)

    for name, calls in calls.items():
        for call in calls:
            retval = call.get('return', '{{void}}')
            c.execute(
                "INSERT INTO `function_calls` values (?, ?, ?, ?, ?)",
                (name, call['parameters'], retval, call['definition_filename'], call['line_number'])
            )

    conn.commit()

def trace_and_profile_from_timestamp(traceDir, timestamp):
    return (
        os.path.join(traceDir, "{}.xt".format(timestamp)),
        os.path.join(traceDir, "{}.xp".format(timestamp))
    )

def create_trace(traceFile, profileFile):
    function_mappings = PHPProfileParser.get_function_file_mapping(profileFile)
    return PHPTraceTokenizer.Trace(traceFile, function_mappings)

def remove_trace_and_profile_data(tracePath, profilePath):
    if os.path.exists(tracePath):
        print("Removing {}".format(tracePath))
        os.unlink(tracePath)

    if os.path.exists(profilePath):
        print("Removing {}".format(profilePath))
        os.unlink(profilePath)

def insert_timestamp_in_db(conn, timestamp, autoRemove=False):
    start_time = time.time()
    traceFile, profileFile = trace_and_profile_from_timestamp(traceDir, timestamp)

    if not timestamp_exists(timestamp, conn):
        trace = create_trace(traceFile, profileFile)
        insert_trace(trace, conn)
        insert_timestamp(timestamp, conn)
        elapsed_time = time.time() - start_time
        print("Took {} milliseconds to process timestamp --{}--".format(timestamp))
        remove_trace_and_profile_data(traceFile, profileFile)
    else:
        print("This timestamp has already been processed!")
        remove_trace_and_profile_data(traceFile, profileFile)

if __name__ == '__main__':
    args = parser.parse_args()
    db_name = args.db

    if not os.path.exists(db_name):
        set_up_db(db_name)

    if args.timestamp:
        with sqlite3.connect(db_name) as conn:
            insert_timestamp_in_db(conn, args.timestamp, args.autoRemove)

    if args.autoImport:
        files = [file.replace(".xp", "").replace(".xt", "") for file in os.listdir(traceDir) if file.endswith("xp") or file.endswith("xt")]
        for timestamp, count in Counter(files).items():
            if count == 2 and re.match(r"\d+", timestamp):
                print("Found timestamp --{}--".format(timestamp))
                with sqlite3.connect(db_name) as conn:
                    try:
                        insert_timestamp_in_db(conn, timestamp, args.autoRemove)
                    except Exception as e:
                        print("Error while processing, moving on to the next")
                        traceback.print_exc()
                print("Done processing timestamp --{}--\n".format(timestamp))
            # else:
            #     print("Invalid timestamp:", timestamp)
