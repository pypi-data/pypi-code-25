import collections
from builtins import zip


def iterable_from(arg):
    """Returns iterable over a single element or iterable"""
    if isinstance(arg, collections.Iterable):
        return arg
    else:
        return arg,


def ibatch(iterable, batch_size):
    """Collect data into fixed-length chunks"""
    return zip(*[iterable] * batch_size)
