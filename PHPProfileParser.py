"""A very use-case specific cachegrind profiler that will only attempt
to compile a dictionary of function names to their file definitions.
Nothing else."""

import re
import sys
from pprint import pprint


class PHPProfilerParser:
    def __init__(self):
        self.fnRegex = re.compile("fn=\((?P<num>\d+)\)( (php::)?(?P<fn>.+))?")
        self.flRegex = re.compile("fl=\((?P<num>\d+)\)( (?P<fl>.+))?")
        self.fnflRegex = re.compile("f[nl]=f[nl]=\((?P<num>\d+)\)")

        self.context = None

        self.files = {}
        self.functions = {}


    def parse(self, filename):
        for line in open(filename):
            self.consume_line(line)

    def consume_line(self, line):
        line = line.replace("\x00", "")

        try:
            if line == '\n':
                # blank line
                return

            firstfour = line[:4]

            if firstfour == "fn=f" or firstfour == "fl=f":
                fnfl = self.fnflRegex.match(line)
                num = fnfl.group('num')
                self.context = num

                return

            if firstfour == "fl=(":
                fl = self.flRegex.match(line)
                filename = fl.group('fl')
                num = fl.group('num')
                if filename:
                    self.files[num] = filename
                self.context = num

                return

            if firstfour == "fn=(":
                fn = self.fnRegex.match(line)
                func = fn.group('fn')
                num = fn.group('num')
                if func:
                    self.functions[num] = (func, self.files[self.context])
        except Exception as e:
            print("Something went wrong while parsing the following line:")
            print(line)
            raise e


def get_function_file_mapping(filenames):
    parser = PHPProfilerParser()

    for filename in filenames:
        parser.parse(filename)

    mapping = {
        "require": "php::internal",
        "require_once": "php::internal",
        "include": "php::internal",
        "include_once": "php::internal"
    }
    for (func, file) in parser.functions.values():
        mapping[func] = file

    return mapping


if __name__ == "__main__":
    filename = sys.argv[1]

    get_function_file_mapping(filename)

    # pprint(parser.functions)
