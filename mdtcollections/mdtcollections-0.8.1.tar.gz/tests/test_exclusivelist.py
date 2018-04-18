import pytest
from mdtcollections import ExclusiveList

from .fixtures import *


def test_exclusive_list_keys(exclusive_list_by_len):
    ll = exclusive_list_by_len
    assert ll == ['a', 'bb']


    with pytest.raises(KeyError):
        ll.append([1])  # already something w/ length 1

    with pytest.raises(KeyError):
        ll.append('e')  # already something w/ length 1

    with pytest.raises(KeyError):
        ll.append('*d')  # already something w/ length 2

    ll.append(b'eee')

    with pytest.raises(KeyError):
        ll.append('*&(')  # already something w/ length 2

    assert len(ll) == 3


def test_exclusive_list_exclusivity(exclusive_list_by_identity):
    ll = exclusive_list_by_identity
    assert ll == list(range(10))

    with pytest.raises(KeyError):
        ll.append(0)

    with pytest.raises(KeyError):
        ll.insert(5, 0)

    with pytest.raises(KeyError):
        ll.extend([9, 10, 11])

    with pytest.raises(KeyError):
        ll[4] = 0

    with pytest.raises(KeyError):
        ll[4:8] = [0]


def test_list_methods():  # a quick tour of normal list behavior
    ll = ExclusiveList()
    ll.append('a')
    ll.append('b')
    assert ll == ['a', 'b']

    ll.extend([1, 2, 3])  # a b 1 2 3
    assert ll == ['a', 'b', 1, 2, 3]
    ll.insert(0, 'inserted')  # inserted a b 1 2 3
    assert ll == ['inserted', 'a', 'b', 1, 2, 3]

    ll.insert(2, 'middle')  # inserted a middle b 1 2 3
    assert ll == ['inserted', 'a', 'middle', 'b', 1, 2, 3]

    assert ll.pop() == 3  # inserted a middle b 1 2
    assert ll == ['inserted', 'a', 'middle', 'b', 1, 2]
    ll.remove(1)
    assert ll == ['inserted', 'a', 'middle', 'b', 2]

    ll[2:4] = range(5, 10)
    assert ll == ['inserted', 'a', 5, 6, 7, 8, 9, 2]

    # and finally, check that it didn't lose track of any keys
    for item in ll:
        with pytest.raises(KeyError):
            ll.append(item)

    # and that deleted keys were truly deleted
    for item in ['middle', 'b', 1, 3]:
        ll.append(item)
