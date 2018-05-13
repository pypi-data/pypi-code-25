# coding=utf-8
import os

ALLOWED_TYPES = (int, float, str, bool, dict)
TRUTHY_VALUES = ('T', 'True', 'true', 'TRUE', 'Y', 'YES', 'Yes', 'yes', '1',)
FALSY_VALUES = ('F', 'False', 'false', 'FALSE', 'N', 'NO', 'No', 'no', '0', '')


class IncompatibleTypeError(TypeError):
    def __init__(self, t, k):
        super(TypeError, self).__init__('Incompatible type {} for key'.format(t, k))


def build_name(key, prefix, force_uppercase, separator):
        key = key.upper() if force_uppercase else key
        prefix = prefix.upper() if force_uppercase else prefix
        return key if not prefix else '{}{}{}'.format(prefix, separator, key)


def parse_bool(value):
    if value in TRUTHY_VALUES:
        return True

    if value in FALSY_VALUES:
        return False

    raise ValueError('Cannot convert "{}" to bool.'.format(value))


def validate_types(key, value):
    if value is None or value is type(None):
        value = str

    value_type = value if value in ALLOWED_TYPES else type(value)
    if value_type not in ALLOWED_TYPES:
        raise IncompatibleTypeError(value_type, key)

    key_type = type(key)
    if key_type is not str:
        raise IncompatibleTypeError(key_type, key)

    return key_type, value_type


def load_from_environment(proto, prefix='', force_uppercase=True, separator='_'):
    def traverse(branch, path):
        result = {}

        for key, value in branch.items():
            _, value_type = validate_types(key, value)

            varname = build_name(key, path, force_uppercase, separator)

            if value_type is dict:
                result[key] = traverse(value, varname)
                continue

            envvalue = os.environ[varname]
            if value_type is bool:
                envvalue = parse_bool(envvalue)
            else:
                envvalue = value_type(envvalue)

            result[key] = envvalue

        return result

    return traverse(proto, prefix)


def dump(config, prefix='', force_uppercase=True, separator='_'):
    variables = {}

    def traverse(branch, path):
        for key, value in branch.items():
            _, value_type = validate_types(key, value)

            varname = build_name(key, path, force_uppercase, separator)

            if value_type is dict:
                traverse(value, varname)
                continue

            variables[varname] = str(value)

    traverse(config, '')
    return variables
