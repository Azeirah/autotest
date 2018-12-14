"""Functions to analyse parsed PHP traces with."""
from pprint import pprint
from collections import namedtuple

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

    # main is recorded as a function call
    calls[0]['return'] = ''

    return calls


def ordered_function_calls(trace):
    calls = []

    for field, i in trace.visit(lambda f: filter_entry(f) or filter_return(f)):
        if filter_entry(field):
            calls.insert(field.function_num, {
                'name': get_fn_name(field.function_name),
                'parameters': field.params,
                'calling_filename': str(field.filename),
                'definition_filename': str(field.definition_filename),
                'line_number': field.line_number,
                'return': '{{void}}'
            })
        elif filter_return(field):
            retval = getattr(field, 'return_value', '{{void}}')

            calls[field.function_num]['return'] = retval

    calls[0]['return'] = '{{void}}'

    return calls


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
