""" Package level utils."""

import shlex


def parse_kv_pairs(key_value_string):
    """ Parse string of key value pairs to dict

    Example:
        'key1=value1 "key 2"="value 2"' --> {'key1': value1, 'key 2': 'value 2'}
        parse(s)
    """
    if not key_value_string:
        return {}
    return dict(token.split('=') for token in shlex.split(key_value_string))
