"""Functions to analyse parsed PHP traces with."""

def filter_entry(node):
    """Filters on nodes of type entry"""
    return node.type == "Entry"

def get_fn_name(fn):
    """Display the field.function_name property"""
    if '->' in fn:
        return fn.split('->')[-1]
    elif '::' in fn:
        return fn.split('::')[-1]
    return fn


def indent_level(level):
    """Displayer for the field.level property"""
    indentation_depth = 2

    indent = " " * indentation_depth

    return indent * (level - 1)


def display_call_tree(trace):
    for field, i in trace.visit(filter_entry):
        print(indent_level(field.level), i, "{0}:{1}@{2}".format(field.filename.stem, field.linenumber, get_fn_name(field.function_name)))


def display_all_functions(trace):
    for field, i in trace.visit(filter_entry):
        print(indent_level(field.level), i, field)
