import collections

from .descriptors import Alias

class DotDict(object):
    """ An attribute-accessible dictionary that preserves insertion order
    """
    def __init__(self, *args, **kwargs):
        self._od = collections.OrderedDict(*args, **kwargs)
        self._init = True

    def __delattr__(self, item):
        if not self.__dict__.get('_init', False):
            super().__delattr__(item)
        else:
            try:
                del self._od[item]
            except KeyError:
                raise AttributeError()

    def __delitem__(self, key):
        if not self.__dict__.get('_init', False):
            raise TypeError()
        else:
            del self._od[key]

    def __dir__(self):
        return list(self.keys()) + super().__dir__()

    def __getstate__(self):
        return {'od': self._od}

    def __setstate__(self, state):
        self._od = state['od']
        self._init = True

    def copy(self):
        return self.__class__(self._od.copy())

    def copydict(self):
        """ Returns a copy of the core dictionary in its native class
        """
        return self._od.copy()

    def __eq__(self, other):
        try:
            return self._od == other._od
        except AttributeError:
            return False

    def __repr__(self):
        return str(self._od).replace('OrderedDict', self.__class__.__name__)

    def __getattr__(self, key):
        if not self.__dict__.get('_init', False):
            return self.__getattribute__(key)
        if key in self._od:
            return self._od[key]
        else:
            raise AttributeError(key)

    def __setattr__(self, key, val):
        if not self.__dict__.get('_init', False):
            super().__setattr__(key, val)
        else:
            self._od[key] = val

    def __bool__(self):
        return bool(self._od)

    __nonzero__ = __bool__


for _v in ('keys values items __iter__ __getitem__  __len__ __contains__ clear '
           ' __setitem__ pop setdefault get update').split():
    setattr(DotDict, _v, Alias('_od.%s' % _v))