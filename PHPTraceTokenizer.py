"""
Parse php xdebug traces.

Needs the following configuration in php.ini
[xdebug]
# set either this or xdebug trace trigger
xdebug.auto_trace=1

xdebug.collect_params=3
xdebug.trace_format=1
xdebug.collect_return=1
xdebug.trace_output_name={set an appropriate directory}

Find more info on these here: https://xdebug.org/docs/all_settings
"""

from pathlib import Path


class Field:
    @property
    def type(self):
        return type(self).__name__


class Entry(Field):
    def __init__(self, fields, function_mappings):
        self.level = int(fields[0])
        """the stack-depth starting at 0"""

        self.function_num = int(fields[1])
        """Each individual function invocation gets a unique index that can be matched to its Return"""

        self.time_index = float(fields[3])
        """Time in milliseconds since starting the trace    sampled at function-start"""

        self.memory = fields[4]
        """Memory usage in bytes before starting this function"""

        self.function_name = fields[5]
        """The function's defined name, anonymous functions are {closure:PATH:linenums}"""

        self.is_function_user_defined = fields[6] == "1"
        """Whether the function is part of std-lib, or defined in php
        Beware: Is true for functions defined in external libraries"""

        self.include_filename = Path(fields[7])
        """If the function is require/include, this field has the value of the path included/required"""

        self.filename = Path(fields[8])
        """Filename where the function got called"""

        self.line_number = fields[9]
        """Line number where the function definition starts"""

        self.params = fields[11:]
        """All parameters of the function"""

        self.definition_filename = function_mappings.get(fields[5], "{{missing file}}")
        """Where the called function is defined"""


class Exit(Field):
    def __init__(self, fields):
        self.level = int(fields[0])
        self.function_num = int(fields[1])
        self.time_index = float(fields[3])
        self.memory = fields[4]


class Return(Field):
    def __init__(self, fields):
        self.level = int(fields[0])
        self.function_num = int(fields[1])
        self.return_value = fields[5]


class Trace:
    def __init__(self, path, function_mappings):
        self.path = path
        self.function_mappings = function_mappings

    def visit(self, filterfn):
        for i, field in enumerate(self.parse()):
            if filterfn(field):
                yield (field, i)

    def parse(self):
        with open(self.path, encoding="utf-8", errors="ignore") as f:
            for r in f.readlines():
                info = r.split("\t")
                num_fields = len(info)
                try:
                    if num_fields == 5:
                        yield Exit(info)
                    elif num_fields == 6:
                        yield Return(info)
                    elif num_fields >= 11:
                        yield Entry(info, self.function_mappings)
                    else:
                        if ("Version" not in r
                                and "File format" not in r
                                and "TRACE START" not in r
                                and "TRACE END" not in r
                                and r != "\n"):
                            print("Unknown type field", r)
                            pass
                except Exception as e:
                    pass
                    # print("parsing error")
                    # raise e
                    # missed node.. parsing error

    # def listElements(self):
    #     elements = set()
    #     with open(self.path, encoding="utf-8", errors="ignore") as f:
    #         for line in f.readlines():
    #             [elements.add(r) for r in re.findall(self.re_elements, line)]
    #     return elements

    # def listFiles(self):
    #     files = set()
    #     with open(self.path, encoding="utf-8", errors="ignore") as f:
    #         for line in f.readlines():
    #             [files.add(r) for r in re.findall(self.re_phpfiles, line)]
    #     return files

# def f(field):
#     return (
#         field.type == "Entry"
#         and
#         ("callback" in field.filename.name.lower()
#             or "outlook" in field.filename.name.lower())
#         and field.is_function_user_defined
#         and "Raven" not in field.function_name
#         and "Doctrine" not in field.function_name
#         and "Zend" not in field.function_name
#         and "Composer" not in field.function_name
#         and "ClassLoader" not in field.function_name
# # and "project_103" in field.filename.name
# # and "agenda" in field.filename.name
# )
#     return (
#         field.type == "Entry"
#         and field.is_function_user_defined
#         and "actinum" in field.function_na):
# me
#         and "studiov6" not in field.filename.name
#         )
