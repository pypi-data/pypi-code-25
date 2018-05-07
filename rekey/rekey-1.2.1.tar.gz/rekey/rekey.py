import __builtin__

from pluckit.pluckit import pluckit


def rekey(obj, key_handle, value_handle = None):
    if obj is None:
        # nothing to rekey
        return None

    if key_handle is None and value_handle is None:
        # nothing to do, so bail
        return obj

    # validate input type
    supported_types = [ list, dict, set, tuple ]
    if not any([ isinstance(obj, t) for t in supported_types ]):
        raise ValueError('type not supported: %s' % type(obj))

    # determine return type
    if key_handle or hasattr(obj, 'keys'):
        res = {}
    else:
        res = []

    # figure out how to iterate
    if hasattr(obj, 'items'):
        _iter = obj.items()
    else:
        _iter = obj

    # determine how to unpack items into key / value pairs
    if hasattr(obj, 'keys'):
        kv_fn = lambda items: items
    else:
        # no key, only value
        kv_fn = lambda items: (None, items)

    # rekey
    for items in _iter:
        # unpack key / value tuple
        key, value = kv_fn(items)

        # set default result values
        new_key, new_value = key, value

        # grab new key / value
        if key_handle != None:
            new_key = pluckit(value, key_handle)

        if value_handle != None:
            new_value = pluckit(value, value_handle)

        # store results
        if type(res) == list:
            res.append(new_value)
        else:
            res[new_key] = new_value

    return res
