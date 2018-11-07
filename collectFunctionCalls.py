#!/usr/bin/python3

"""
Given a parsed PHP trace (PHPTrace.py@Trace)
This file will parse all function calls, with their parameters and their respective return values.
"""

import argparse
import sqlite3
import os.path

import PHPTraceParser
import PHPTraceTokenizer
import PHPProfileParser

from settings import *


parser = argparse.ArgumentParser(description="Add function-call-parameters to a database")
parser.add_argument('timestamp', type=str, help="trace timestamp")
args = parser.parse_args()


tracefile = os.path.join(traceDir, "{}.xt".format(args.timestamp))
profileFile = os.path.join(traceDir, "{}.xp".format(args.timestamp))

function_mappings = PHPProfileParser.get_function_file_mapping(profileFile)
trace = PHPTraceTokenizer.Trace(tracefile, function_mappings)

def set_up_db(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    with open('schema.sql') as f:
        c.execute(f.read())
    conn.commit()
    conn.close()

if __name__ == '__main__':
    db_name = 'function-calls.db'

    if not os.path.exists(db_name):
        set_up_db(db_name)

    conn = sqlite3.connect(db_name)

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
    conn.close()
