import pickle
import types


def make_callable(value, call):
    try:
        value_type = value.__class__
    except AttributeError:
        value_type = type(value)
    cls_name = 'Callable{cls}'.format(cls=value_type.__name__.capitalize())
    bases = _Bool if value_type is bool else value_type,
    attributes = {
        '__call__': call, '__class__': value_type,
        '__iadd__': lambda _, other: value + other
    }
    callable_type = type(cls_name, bases, attributes)
    try:
        reduce = pickle.Pickler.dispatch[value_type]
        pickle.Pickler.dispatch[callable_type] = reduce
    except (AttributeError, KeyError):
        pass
    callable_value = callable_type(value)
    for attr_name in dir(value):
        try:
            if attr_name not in attributes:
                setattr(callable_value, attr_name, getattr(value, attr_name))
        except AttributeError:
            pass
    return callable_value


class property(property):
    def __init__(self, fget=None, fset=None, fdel=None, fcall=None, doc=None):
        super(property, self).__init__(fget, fset, fdel, doc)
        self.fcall = fcall

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        if self.fget is None:
            raise AttributeError('unreadable attribute')

        if self.fcall is None and self.fset is None:
            return self.fget(obj)

        value = self.fget(obj)
        fcall = types.MethodType(self.fcall or self.fset, obj)

        return make_callable(value, fcall)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.fcall, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.fcall, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.fcall, self.__doc__)

    def caller(self, fcall):
        return type(self)(self.fget, self.fset, self.fdel, fcall, self.__doc__)


class _Bool(object):
    def __init__(self, value):
        if not isinstance(value, bool):
            raise ValueError
        self.value = value

    def __bool__(self):
        return self.value

    __nonzero__ = __bool__
