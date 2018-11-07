"""A very use-case specific cachegrind profiler that will only attempt
to compile a dictionary of function names to their file definitions.
Nothing else."""

import re
import sys
from pprint import pprint


class Function:
    def __init__(self):
        # self.line = -1
        self.fn = ""
        self.fl = ""


class PHPProfilerParser:
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename)

        # None before starting
        # "metadata" while parsing metadata
        # and
        # "body" while parsing the actual profiling data
        self.currentParsingSection = "metadata"

        self.fnRegex = re.compile("^fn=\((?P<num>\d+)\)( (php::)?(?P<fn>.+))?$")
        self.flRegex = re.compile("^fl=\((?P<num>\d+)\)( (?P<fl>.+))?$")
        self.fnflRegex = re.compile("^f[nl]=f[nl]=\((?P<num>\d+)\)")

        self.files = {}
        self.functions = {}


    def parse(self):
        while not self.consume_line():
            pass


    def consume_line(self):
        line = self.file.readline()
        # print(line)
        # metadata contains ":"
        if self.currentParsingSection == "metadata" and (":" in line or len(line) == 1):
            # noop for metadata, don't really care about it for our use-case
            pass
        else:
            self.currentParsingSection = "body"

        if line == '\n':
            # blank line
            self.context = Function()

        if line.startswith("fn=fl") or line.startswith("fl=fl"):
            fnfl = self.fnflRegex.match(line)
            num = fnfl.group('num')
            self.context.fl = num

            return False

        if line.startswith("fl"):
            fl = self.flRegex.match(line)
            filename = fl.group('fl')
            num = fl.group('num')
            if filename:
                self.files[num] = filename
            self.context.fl = num

        if line.startswith("fn"):
            fn = self.fnRegex.match(line)
            func = fn.group('fn')
            num = fn.group('num')
            if func:
                self.functions[num] = (func, self.files[self.context.fl])

        return "{main}" in line


def get_function_file_mapping(filename):
    parser = PHPProfilerParser(filename)

    parser.parse()

    mapping = {
        "require": "php::internal",
        "require_once": "php::internal",
        "include": "php::internal",
        "include_once": "php::internal"
    }
    for k, (func, file) in parser.functions.items():
        mapping[func] = file

    return mapping


if __name__ == "__main__":
    filename = sys.argv[1]

    get_function_file_mapping(filename)

    # pprint(parser.functions)
