from itertools import iteritems


def reverse(mapping):
    """
    Returns a new dictionary with keys and values swapped.

        >>> reverse({1: 2, 3: 4})
        {2: 1, 4: 3}
    """
    return dict([(value, key) for (key, value) in iteritems(mapping)])


def find(dictionary, element):
    """
    Returns a key whose value in `dictionary` is `element`
    or, if none exists, None.

        >>> d = {1:2, 3:4}
        >>> find(d, 4)
        3
        >>> find(d, 5)
    """
    for (key, value) in iteritems(dictionary):
        if element is value:
            return key


