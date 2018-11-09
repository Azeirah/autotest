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

parser = argparse.ArgumentParser(description="Add function-call-parameters to a database")
parser.add_argument('trace', type=str, help="trace filename")
args = parser.parse_args()


trace = PHPTraceTokenizer.Trace(args.trace)

if __name__ == '__main__':
    db_name = 'function-calls.db'

    conn = sqlite3.connect(db_name)

    c = conn.cursor()
    calls = PHPTraceParser.grouped_function_calls(trace)

    for name, calls in calls.items():
        for call in calls:
            retval = call.get('return', '{{void}}')
            c.execute(
                "INSERT INTO `function_calls` values (?, ?, ?, ?, ?)",
                (name, call['parameters'], retval, call['filename'], call['line_number'])
            )

    conn.commit()
    conn.close()
