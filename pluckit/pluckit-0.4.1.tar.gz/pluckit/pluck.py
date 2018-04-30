from copy import copy

from .pluckit import pluckit


__all__ = [ 'pluck' ]


def pluck(collection, handle):
    if collection is None:
        # nothing to pluck
        return None

    if isinstance(collection, dict):
        if type(collection) == dict:
            clone = {}
        else:
            # preserve class type and attributes
            clone = copy(collection)
            clone.clear()

        clone.update(
            { k : pluckit(v, handle) for k,v in collection.items() }
        )
        return clone

    if isinstance(collection, set):
        if type(collection) == set:
            clone = set()
        else:
            # preserve class type and attributes
            clone = copy(collection)
            clone.clear()

        clone.update({ pluckit(x, handle) for x in collection })
        return clone

    if isinstance(collection, tuple):
        # can't clone, but use same class as return type
        return collection.__class__(
            [ pluckit(x, handle) for x in collection ]
        )

    if isinstance(collection, list) or hasattr(collection, '__iter__'):
        # list or list like

        if type(collection) == list:
            clone = []
        elif hasattr(collection, '__delslice__') or hasattr(collection, 'delslice'):
            # preserve class type and attributes
            clone = copy(collection)
            del clone[0:]
        else:
            # fall back to regular list
            clone = []

        clone += [ pluckit(x, handle) for x in collection ]
        return clone

    raise TypeError('unpluckable type: %s' % type(collection))
