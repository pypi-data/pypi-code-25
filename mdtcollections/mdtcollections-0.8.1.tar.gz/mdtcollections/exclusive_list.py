import collections

class ExclusiveList(collections.UserList):
    """ Behaves like a list, but won't allow duplicate items to be added.

    Unlike an OrderedDict, this allows all normal list methods and retains normal their
    time complexity.

    Two items are considered "duplicates" here if they compare equal.
    A "key" callable may be passed to create keys that determine equality.

    Raises:
        KeyError: upon attempts to add duplicate objects
        TypeError: upon attempts to add unhashable objects to the list

    Notes:
        Key functions may be recomputed. If your key function is slow, you should
        add memoization.

    Args:
        iterable (Iterable): items to initialize the list
        key (callable): callable that accepts a single item in the list and returns an
                        object to use for equality comparisons.
    """
    def __init__(self, iterable=None, key=None):
        super(ExclusiveList, self).__init__()
        self._keys = set()
        self._keyfn = self._identity if key is None else key
        if iterable is not None:
            self.extend(iterable)

    def _validate_new_keys(self, iterable):
        keys = set(map(self._keyfn, iterable))
        if len(keys) < len(iterable):
            raise KeyError('Duplicate keys in passed object!')
        collision = keys.intersection(self._keys)
        if collision:
            raise KeyError('Keys already exist: %s' % ','.join(map(str, collision)))
        return keys

    def append(self, obj):
        keys = self._validate_new_keys([obj])
        super(ExclusiveList, self).append(obj)
        self._keys.update(keys)

    def extend(self, iterable):
        items = list(iterable)
        keys = self._validate_new_keys(items)
        super(ExclusiveList, self).extend(items)
        self._keys.update(keys)

    def insert(self, index, obj):
        self[index: index] = [obj]  # just delegate to __setitem__

    def clear(self):
        self._keys.clear()
        super(ExclusiveList, self).clear()

    @staticmethod
    def _identity(obj):
        return obj

    def __setitem__(self, index, objs):
        if not isinstance(index, slice):
            objs = [objs]
            index = slice(index, index+1)
        removekeys = set(map(self._keyfn, self[index]))
        candidate_keys = (self._keys - removekeys)
        newkeys = set(map(self._keyfn, objs))
        collision = candidate_keys.intersection(newkeys)

        if collision:
            raise KeyError('Keys already exist: %s' % ','.join(map(str, collision)))

        super(ExclusiveList, self).__setitem__(index, objs)
        self._keys.clear()
        self._keys.update(newkeys)
        self._keys.update(candidate_keys)

    def remove(self, obj):
        idx = self.index(obj)
        self.pop(idx)

    def pop(self, index=None):
        if index is None:
            index = len(self) - 1

        key = self._keyfn(self[index])
        assert key in self._keys, "Keys and list are inconsistent"
        obj = super(ExclusiveList, self).pop(index)
        self._keys.remove(key)
        return obj
