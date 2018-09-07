#!/usr/bin/python3

import argparse
import PHPTraceTokenizer
import cmd
import PHPTraceParser
import sys


class PHPTraceAnalyser(cmd.Cmd):
    """Interactive interface for analysing PHP traces"""

    intro = "Analyse php traces, run `setup` for installation instructions, or run `introduction` to get started\notherwise; run `help` to list all supported commands."
    ruler = ""

    def __init__(self, args):
        """Initialize the cli-loop"""
        super().__init__()
        self.args = args

        self.trace = PHPTraceTokenizer.Trace(args.trace)

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
xdebug.trace_format=1
xdebug.collect_return=1
xdebug.trace_output_name={set an appropriate directory}

You can find additional info on xdebug configuration parameters here
https://xdebug.org/docs/all_settings

After you've finished configuring php, you can get started analysing.
Run do_introduction next for help on running the php analyser
""")

    def do_introduction(self, line):
        """Shows an introduction to this CLI"""

        print("""Todo, there isn't much to this CLI for now, only
call_tree is interesting""")

    def do_show_file(self, line):
        """Prints the loaded file"""
        print(args.trace)

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
                retval = call['return']
                parameters = call['parameters']

                if not parameters:
                    parameters = '{{arity-0}}'

                if not retval:
                    retval = '{{void}}'

                formatted_call = "{params:40}->\t{ret}".format(
                    params=parameters,
                    ret=retval
                )

                print(formatted_call)

            print("\n")


parser = argparse.ArgumentParser(description="Dig up wonderful info from trace files")
parser.add_argument('trace', type=str, help="trace filename")

args = parser.parse_args()


if __name__ == '__main__':
    if len(sys.argv) > 2:
        PHPTraceAnalyser(args).onecmd(' '.join(sys.argv[2:]))
    else:
        PHPTraceAnalyser(args).cmdloop()
