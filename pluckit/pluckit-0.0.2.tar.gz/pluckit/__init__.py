__author__ = 'dpepper'
__version__ = '0.0.2'


from copy import copy
from types import *


__all__ = [ 'Pluckable', 'pluckit' ]



class Pluckable():
    def pluck(self, *handles):
        if isinstance(self, list):
            if type(self) == list:
                clone = []
            else:
                clone = copy(self)
                [ clone.pop() for x in xrange(len(clone)) ]

            clone += [ pluckit(x, *handles) for x in self ]
            return clone

        if isinstance(self, dict):
            # use empty clone so we preserve class properties
            if type(self) == dict:
                clone = {}
            else:
                clone = copy(self)
                clone.clear()

            clone.update(
                { k : pluckit(v, *handles) for k,v in self.items() }
            )
            return clone

        if isinstance(self, set):
            if type(self) == set:
                clone = set()
            else:
                clone = copy(self)
                clone.clear()

            clone.update({ pluckit(x, *handles) for x in self })
            return clone

        raise TypeError('unpluckable type: %s' % type(self))


def pluckit(obj, *handles):
    if obj == None:
        raise ValueError("there's nothing to pluck")

    if len(handles) == 0:
        raise ValueError("you've got to pluck something")

    if len(handles) == 1:
        return __pluck_single(obj, handles[0])
    else:
        return [ __pluck_single(obj, handle) for handle in handles ]


def __pluck_single(obj, handle):
    # function pointer
    if callable(handle):
        return handle(obj)

    # dict-like key
    if hasattr(obj, 'has_key'):
        return obj[handle]

    # object attribute or class method
    if type(handle) == str and hasattr(obj, handle):
        # make sure it's a class method, not a legit returned callable
        attr = getattr(obj, handle)

        if isinstance(attr, (
            BuiltinFunctionType, BuiltinMethodType,
            FunctionType, MethodType,
        )):
            # use method's return value
            return attr()

        # class attribute
        return attr

    # list-like index
    if hasattr(obj, '__getitem__') and isinstance(handle, int):
        return obj[handle]

    raise TypeError('invalid handle: %s' % handle)
