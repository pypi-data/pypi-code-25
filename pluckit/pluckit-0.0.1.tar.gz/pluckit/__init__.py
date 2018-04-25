__author__ = 'dpepper'
__version__ = '0.0.1'


from types import *


__all__ = [ 'pluckit', 'Pluckable' ]



def pluckit(obj, *handles):
    if obj == None:
        raise ValueError("there's nothing to pluck")

    if len(handles) == 0:
        raise ValueError("you've got to pluck something")

    if len(handles) == 1:
        return __pluck_single(obj, handles[0])
    else:
        return [ __pluck_single(obj, handle) for handle in handles ]


class Pluckable():
    def pluck(self, *handles):
        return pluckit(self, *handles)


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
            property
        )):
            # use method's return value
            return attr()

        # class attribute
        return attr

    # list-like index
    if hasattr(obj, '__getitem__'):
        return obj[handle]

    raise TypeError('invalid handle: %s' % handle)
