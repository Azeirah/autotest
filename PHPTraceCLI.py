#!/usr/bin/python3

import argparse
import os

import PHPTraceTokenizer
import PHPProfileParser
import cmd
import PHPTraceParser
import sys

traceDir = "trace-data"


class PHPTraceAnalyser(cmd.Cmd):
    """Interactive interface for analysing PHP traces"""

    intro = "Analyse php traces, run `setup` for installation instructions, or run `introduction` to get " \
            "started\notherwise; run `help` to list all supported commands. "
    ruler = ""

    def __init__(self, args):
        """Initialize the cli-loop"""
        super().__init__()
        self.args = args

        if args.timestamp == 'latest':
            files = os.listdir(traceDir)
            timestamps = sorted([int(stamp.split(".")[0]) for stamp in files if '.x' in stamp], reverse=True)
            args.timestamp = timestamps[0]
            print(args.timestamp)

        tracefile = os.path.join(traceDir, "{}.xt".format(args.timestamp))
        profileFile = os.path.join(traceDir, "{}.xp".format(args.timestamp))

        function_mappings = PHPProfileParser.get_function_file_mapping(profileFile)
        self.trace = PHPTraceTokenizer.Trace(tracefile, function_mappings)

    def do_exit(self, line):
        """Exit the cli"""
        sys.exit()

    def do_quit(self, line):
        """Exit the cli"""
        sys.exit()

    def do_setup(self, line):
        """Shows instructions on how to set-up and install tracing"""

        print("""This is a command-line interface application built
to analyse php traces. That is, xdebug .xt files, not stack traces!

To get started, you need to install xdebug and configure your php.ini

[PHP]
...
# configure your extension, path is liiikely different
zend_extension=/usr/lib/php/20151012/xdebug.so

[xdebug]
xdebug.auto_trace=1
xdebug.collect_params=3
xdebug.trace_output_dir=/home/mb/Documents/autotest/trace-data/
xdebug.trace_format=1
xdebug.collect_return=1
xdebug.trace_output_name="%t"

xdebug.profiler_enable=1
xdebug.profiler_output_dir=/home/mb/Documents/autotest/trace-data/
xdebug.profiler_output_name="%t.xp"

You can find additional info on xdebug configuration parameters here
https://xdebug.org/docs/all_settings

Note that all the above parameters are required for this program to run properly
There might be some parameter configurations that will work fine as well, don't change
the default parameters unless you have some time to waste.

After you've finished configuring php, you can get started analysing.
Run do_introduction next for help on running the php analyser
""")

    def do_introduction(self, line):
        """Shows an introduction to this CLI"""

        print("""Todo, there isn't much to this CLI for now, only
call_tree is interesting""")

    def do_call_tree(self, line):
        """Display a simple indented call-tree"""
        PHPTraceParser.call_tree(self.trace)

    def do_function_names(self, line):
        """Display the names of all functions"""
        functions = PHPTraceParser.function_names(self.trace)
        print("\n".join([fn[0] for fn in functions]))

    def do_function_calls(self, line):
        """Display all function calls along with their respective
        parameters and return values"""

        calls = PHPTraceParser.function_calls(self.trace)

        print("\n".join([
            "{name}({params}) -> {ret}".format(
                name=call['name'],
                params=call['parameters'],
                ret=call['return']
            )
            for call in calls
        ]))

    def do_grouped_function_calls(self, line):
        calls = PHPTraceParser.grouped_function_calls(self.trace)

        for name, calls in calls.items():
            print(name)
            print("-" * len(name))

            for call in calls:
                retval = call.get('return', '{{void}}')

                formatted_call = "{params:40}->\t{ret}".format(
                    params=call['parameters'],
                    ret=retval
                )

                print(formatted_call)

            print("\n")


parser = argparse.ArgumentParser(description="Dig up wonderful info from trace files")
parser.add_argument('timestamp', type=str, nargs="?", help="Timestamp of a trace and profile, input 'latest' to pick "
                                                           "the most recent one")
parser.add_argument('--list', dest="list", action="store_true", help="List all potential traces")
args = parser.parse_args()

if __name__ == '__main__':
    if args.list:
        files = os.listdir(traceDir)
        timestamps = set()

        for file in files:
            timestamps.update((file.split(".")[0], ))

        for timestamp in timestamps:
            if "{}.xt".format(timestamp) in files and \
                    "{}.xp".format(timestamp) in files:
                print(timestamp)

        print("latest")
        sys.exit()

    PHPTraceAnalyser(args).cmdloop()
