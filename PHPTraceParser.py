"""Functions to analyse parsed PHP traces with."""
from pprint import pprint


def filter_entry(node):
    """Filters on nodes of type entry"""
    return node.type == "Entry"

def filter_return(node):
    return node.type == "Return"

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
        print(indent_level(field.level), i, "{0}:{1}@{2}".format(field.filename.stem, field.linenumber, get_fn_name(field.function_name)))


def function_names(trace):
    functions = set()
    for field, i in trace.visit(filter_entry):
        functions.add((get_fn_name(field.function_name), ))
        # print(indent_level(field.level), i, get_fn_name(field.function_name))

    return functions


def function_calls(trace):
    calls = []

    stack = []
    for field, i in trace.visit(lambda f: filter_entry(f) or filter_return(f)):
        if filter_entry(field):
            _currentCall = {
                'name': get_fn_name(field.function_name),
                'parameters': ", ".join(field.params).replace('\n', ''),
            }
            stack.append(_currentCall)
            calls.append(_currentCall)
        elif filter_return(field):
            _currentCall = stack.pop()
            _currentCall['return'] = field.return_value.replace('\n', '')

    # main is recorded as a function call
    calls[0]['return'] = ''

    return calls


def grouped_function_calls(trace):
    calls = {}

    stack = []
    for field, i in trace.visit(lambda f: filter_entry(f) or filter_return(f)):
        if filter_entry(field):
            _currentCall = {
                'name': get_fn_name(field.function_name),
                'parameters': ", ".join(field.params).replace('\n', ''),
            }
            stack.append(_currentCall)
            if _currentCall['name'] in calls:
                calls[_currentCall['name']].append(_currentCall)
            else:
                calls[_currentCall['name']] = [_currentCall]
        elif filter_return(field):
            _currentCall = stack.pop()
            _currentCall['return'] = field.return_value.replace('\n', '')

    # main is recorded as a function call
    calls['{main}'][0]['return'] = ''

    return calls


def filenames(trace):
    files = set()

    for field, i in trace.visit(lambda f: filter_entry(f)):
        files.update((str(field.filename), ))

    return files
