from copy import copy

from .pluckit import pluckit


def pluck(collection, *handles):
    if isinstance(collection, dict):
        # use empty clone so we preserve class properties
        if type(collection) == dict:
            clone = {}
        else:
            clone = copy(collection)
            clone.clear()

        clone.update(
            { k : pluckit(v, *handles) for k,v in collection.items() }
        )
        return clone

    if isinstance(collection, set):
        if type(collection) == set:
            clone = set()
        else:
            clone = copy(collection)
            clone.clear()

        if len(handles) <= 1:
            res = { pluckit(x, *handles) for x in collection }
        else:
            # lists are unhashable, so cast to a tuple
            res = { tuple(pluckit(x, *handles)) for x in collection }

        clone.update(res)
        return clone

    if isinstance(collection, list) or hasattr(collection, '__iter__'):
        # list or list like

        if type(collection) == list:
            clone = []
        elif hasattr(collection, '__delslice__') or hasattr(collection, 'delslice'):
            # clone and clear
            clone = copy(collection)
            del clone[0:]
        else:
            # fall back to regular list
            clone = []

        clone += [ pluckit(x, *handles) for x in collection ]
        return clone

    raise TypeError('unpluckable type: %s' % type(collection))
