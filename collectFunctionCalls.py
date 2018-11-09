#!/usr/bin/python3

"""
Given a parsed PHP trace (PHPTraceParser.py@Trace)
This file will parse all function calls, with their parameters and their respective return values.
"""

import argparse
import sqlite3
import os.path

import PHPTraceParser
import PHPTraceTokenizer
import PHPProfileParser

from settings import traceDir


parser = argparse.ArgumentParser(description="Add function-call-parameters to a database")
parser.add_argument('timestamp', type=str, help="trace timestamp")
parser.add_argument('-d', '--db', nargs="?", dest="db", type=str, default="function-calls.db", help="name of the sqlite3 .db file")

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


if __name__ == '__main__':
    args = parser.parse_args()
    db_name = args.db
    timestamp = args.timestamp

    if not os.path.exists(db_name):
        set_up_db(db_name)

    with sqlite3.connect(db_name) as conn:
        if not timestamp_exists(timestamp, conn):
            traceFile, profileFile = trace_and_profile_from_timestamp(traceDir, args.timestamp)
            trace = create_trace(traceFile, profileFile)
            insert_trace(trace, conn)
            insert_timestamp(timestamp, conn)
        else:
            print("This timestamp has already been processed!")
