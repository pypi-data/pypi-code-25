
class Alias(object):
    """
    Descriptor that delegates to a child's attribute or method.
    e.g.
    >>> class A(object):
    >>>     childkeys = Alias('child.keys')
    >>>     child = dict()
    >>>
    >>> a = A()
    >>> a.child['key'] = 'value'
    >>> a.childkeys() # calls a.child.keys(), returns ['key']
    ['key']
    """
    def __init__(self, objattr):
        objname, attrname = objattr.split('.')
        self.objname = objname
        self.attrname = attrname

    def __get__(self, instance, owner):
        if instance is None:
            assert owner is not None
            return _unbound_getter(self.objname, self.attrname)
        else:
            proxied = getattr(instance, self.objname)
            return getattr(proxied, self.attrname)

    def __set__(self, instance, value):
        if instance is None:
            raise NotImplementedError()
        else:
            proxied = getattr(instance, self.objname)
            setattr(proxied, self.attrname, value)


def _unbound_getter(objname, methodname):
    def _method_getter(s, *args, **kwargs):
        obj = getattr(s, objname)
        meth = getattr(obj, methodname)
        return meth(*args, **kwargs)
    return _method_getter


class IndexView(object):
    def __init__(self, attr, index):
        self.attr = attr
        self.index = index

    def __get__(self, instance, owner):
        return getattr(instance, self.attr)[self.index]


class Synonym(object):
    """ An attribute (class or intance) that is just a synonym for another.
    """
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        setattr(instance, self.name, value)


class Attribute(object):
    """For overriding a property in a superclass - turns the attribute back
    into a normal instance attribute"""
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, cls):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        return setattr(instance, self.name, value)
