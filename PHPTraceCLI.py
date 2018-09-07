#!/usr/bin/python3

import argparse
import PHPTrace
import cmd
import PHPTraceAnalysis


class PHPTraceAnalyser(cmd.Cmd):
    """Interactive interface for analysing PHP traces"""

    intro = "Analyse php traces, run `setup` for installation instructions, or run `introduction` to get started"
    ruler = ""

    def __init__(self, args):
        """Initialize the cli-loop"""
        super().__init__()
        self.args = args

        self.trace = PHPTrace.Trace(args.trace)

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
display_call_tree is interesting""")

    def do_show_file(self, line):
        """Prints the loaded file"""
        print(args.trace)

    def do_display_call_tree(self, line):
        """Display a simple indented call-tree"""
        PHPTraceAnalysis.display_call_tree(self.trace)

    def do_display_all_functions(self, line):
        """Display all called functions"""
        PHPTraceAnalysis.display_all_functions(self.trace)


parser = argparse.ArgumentParser(description="Dig up some useful info from trace files")
parser.add_argument('trace', type=str, help="trace filename")

args = parser.parse_args()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        PHPTraceAnalyser().onecmd(' '.join(sys.argv[2:]))
    else:
        PHPTraceAnalyser(args).cmdloop()
