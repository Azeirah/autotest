"""Functions to analyse parsed PHP traces with."""


def get_fn_name(fn):
    if '->' in fn:
        return fn.split('->')[-1]
    elif '::' in fn:
        return fn.split('::')[-1]
    return fn


def display_call_tree(trace):
    for field, i in trace.visit(lambda x: x.type == "Entry"):
        print(field.level * "  ", i, "{0}:{1}@{2}".format(field.filename.stem, field.linenumber, get_fn_name(field.function_name)))
