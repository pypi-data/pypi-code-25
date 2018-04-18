import collections
from mdtcollections import DotDict, Alias, ExclusiveList
import pytest

registered_types = {}


def typedfixture(*types, **kwargs):
    """This is a decorator that lets us associate fixtures with one or more arbitrary types.
    We'll later use this type to determine what tests to run on the result"""

    def fixture_wrapper(func):
        for t in types:
            registered_types.setdefault(t, []).append(func.__name__)
        return pytest.fixture(**kwargs)(func)

    return fixture_wrapper


TESTDICT = collections.OrderedDict((('a', 'b'),
                                    ('c', 3),
                                    ('d', 'e'),
                                    ('a', 1),
                                    (3, 35)))
@typedfixture('pickleable')
def dotdict():
    dd = DotDict(TESTDICT)
    return dd


class ComposedClass(object):
    delegated = Alias('s.lower')

    def __init__(self):
        self.s = 'ABC'


@typedfixture('pickleable')
def class_with_alias():
    return ComposedClass()


@typedfixture('pickleable')
def exclusive_list_by_identity():
    return ExclusiveList(range(10))


@typedfixture('pickleable')
def exclusive_list_by_len():
    return ExclusiveList(['a', 'bb'], key=len)


pickleable = registered_types['pickleable']
