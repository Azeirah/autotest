import re
from collections import namedtuple

# These are, -- and need to be -- exactly the same
# as the values specified in the table
# `value_types` (refer to schema.sql)
PHP_TYPE_NULL = "null"
PHP_TYPE_BOOLEAN = "boolean"
PHP_TYPE_STRING = "string"
PHP_TYPE_INTEGER = "integer"
PHP_TYPE_DOUBLE = "double"
PHP_TYPE_ARRAY = "array"
PHP_TYPE_OBJECT = "object"
PHP_TYPE_UNKNOWN = "unknown"
PHP_TYPE_RESOURCE = "resource"

php_typed_value = namedtuple('php_typed_value', ['value', 'php_type'])

PHP_INST_VOID = php_typed_value(value='NULL', php_type=PHP_TYPE_NULL)

int_regex = re.compile("^-?\d+$")
float_regex = re.compile("^-?(\d+\.\d+)|(INF)$")

def infer_type(value):
    """Takes a value, returns the value along with its inferred type

    >>> infer_type('hi')
    ('hi', PHP_TYPE_STRING)

    >>> infer_type(3)
    (3, PHP_TYPE_INT)
    """

    inferred_type = PHP_TYPE_UNKNOWN

    if value[0] == "'":
        inferred_type = PHP_TYPE_STRING
    elif value.startswith("array "):
        inferred_type = PHP_TYPE_ARRAY
    elif value.startswith("FALSE") or value.startswith("TRUE"):
        inferred_type = PHP_TYPE_BOOLEAN
    elif value.startswith("NULL"):
        inferred_type = PHP_TYPE_NULL
    elif value.startswith("class"):
        inferred_type = PHP_TYPE_OBJECT
    elif value.startswith('resource'):
        inferred_type = PHP_TYPE_RESOURCE
    elif int_regex.match(value):
        inferred_type = PHP_TYPE_INTEGER
    elif float_regex.match(value):
        inferred_type = PHP_TYPE_DOUBLE

    # remove very costly class definition
    # this does mean we'll lose some information
    # about the class instance variables, however.
    if inferred_type == PHP_TYPE_OBJECT:
        value = value.split('{')[0]

    return php_typed_value(value=value, php_type=inferred_type)
