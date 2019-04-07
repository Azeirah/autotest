"""Functions to analyse parsed PHP traces with."""
from pprint import pprint
from collections import namedtuple
from PHPLangUtils import PHP_INST_VOID


def filter_entry(node):
    """Filters on nodes of type entry"""
    return node.type == "Entry"

def filter_return(node):
    return node.type == "Return"

def filter_exit(node):
    return node.type == "Exit"

def get_fn_name(fn):
    """Display the field.function_name property"""
    if '->' in fn:
        return fn.split('->')[-1]
    elif '::' in fn:
        return fn.split('::')[-1]
    return fn


def indent_level(level):
    """Display the field.level property"""
    indentation_depth = 2

    indent = " " * indentation_depth

    return indent * (level - 1)


def call_tree(trace):
    for field, i in trace.visit(filter_entry):
        print(indent_level(field.level), i, "{0}:{1}@{2}".format(field.filename.stem, field.line_number, get_fn_name(field.function_name)))


def function_names(trace):
    functions = set()
    for field, i in trace.visit(filter_entry):
        functions.add((get_fn_name(field.function_name) + "\t" + field.definition_filename, ))
        # print(indent_level(field.level), i, get_fn_name(field.function_name))

    return functions


def function_calls(trace):
    calls = []

    stack = []
    for field, i in trace.visit(lambda f: filter_entry(f) or filter_return(f)):
        if filter_entry(field):
            _currentCall = {
                'name': get_fn_name(field.function_name),
                'parameters': field.params,
            }
            stack.append(_currentCall)
            calls.append(_currentCall)
        elif filter_return(field):
            _currentCall = stack.pop()
            _currentCall['return'] = field.return_value

    try:
        # main is recorded as a function call
        calls[0]['return'] = PHP_INST_VOID
    except KeyError:
        pass

    return calls


def ordered_function_calls(trace):
    calls = {}

    for field, i in trace.visit(lambda _: True):
        if filter_entry(field):
            calls[field.function_num] = {
                'name': get_fn_name(field.function_name),
                'parameters': field.params,
                'calling_filename': str(field.filename),
                'definition_filename': str(field.definition_filename),
                'line_number': field.line_number,
                'return': PHP_INST_VOID,
                'memory_start': field.memory,
                'memory_end': -1,
                'memory_delta': -1,
                'time_start': field.time_index,
                'time_end': -1,
                'time_delta': -1
            }
            # print("entry:", field.function_num)
        elif filter_exit(field):
            # print("exit:", field.function_num)
            calls[field.function_num]['memory_end'] = field.memory
            calls[field.function_num]['time_end'] = field.time_index
            calls[field.function_num]['time_delta'] = field.time_index - calls[field.function_num]['time_start']
            calls[field.function_num]['memory_delta'] = field.memory - calls[field.function_num]['memory_start']
        elif filter_return(field):
            retval = getattr(field, 'return_value', PHP_INST_VOID)

            calls[field.function_num]['return'] = retval

    try:
        # main is recorded as a function call
        calls[0]['return'] = PHP_INST_VOID
    except KeyError:
        pass

    return calls.values()


def grouped_function_calls(trace):
    calls = {}

    stack = []
    for field, i in trace.visit(lambda f: filter_entry(f) or filter_return(f)):
        if filter_entry(field):
            _currentCall = {
                'name': get_fn_name(field.function_name),
                'parameters': field.params,
                'calling_filename': str(field.filename),
                'definition_filename': str(field.definition_filename),
                'line_number': field.line_number
            }

            stack.append(_currentCall)

            if _currentCall['name'] in calls:
                calls[_currentCall['name']].append(_currentCall)
            else:
                calls[_currentCall['name']] = [_currentCall]
        elif filter_return(field):
            _currentCall = stack.pop()

            retval = field.return_value
            if not retval:
                retval = '{{void}}'

            _currentCall['return'] = retval


def filenames(trace):
    files = []

    for field, i in trace.visit(lambda f: filter_entry(f)):
        name = str(field.filename)
        if name not in files:
            files.append(name)

    return files
