
def yaml_unnest(defs, prefix=''):
    stop = lambda x: type(x) is not dict or any((key in x for key in ['description', 'expires', 'kind']))
    new_defs, found = {}, list(defs.iteritems())

    while found:
        key, value = found.pop()
        if stop(value):
            new_defs[key] = value
        else:
            found += [('{}.{}'.format(key, k), v) for k, v in value.iteritems()]

    return new_defs


