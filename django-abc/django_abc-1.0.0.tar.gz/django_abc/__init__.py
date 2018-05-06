import re

from django.db.models import Model

method_name_description_pattern = re.compile(r'([a-zA-Z_]+[a-zA-Z0-9_]*)(\(.*)?')


class _ABC:
    def subclass(self):
        for cls in self.subclasses:
            try:
                return getattr(self, cls.lower())
            except AttributeError:
                pass
        raise TypeError('Could not match subclass')

    def subclass_call(self, name, *args, **kwargs):
        return self.get_method(name)(*args, **kwargs)

    def get_method(self, name):
        try:
            return getattr(self.subclass(), name)
        except AttributeError:
            raise NotImplementedError('{} does not implement {}.{}'.format(self.subclass().__class__, self.__class__, name))

    def subclass_delegator(self, name):
        def the_method(*args, **kwargs):
            return self.subclass_call(name, *args, **kwargs)
        return the_method

    def __getattribute__(self, name):
        if _ABC in super().__getattribute__('__class__').__bases__:
            if name in super().__getattribute__('abstract_names_only'):
                return self.subclass_delegator(name)
        return super().__getattribute__(name)


def base(cls):
    """Decorator for base class"""
    if Model not in cls.__bases__:
        raise TypeError('@Interface should be used on a subclass of django.db.models.Model')
    try:
        abstract_method_descriptions = cls.abstract
    except AttributeError:
        raise TypeError('class decorated with @base should have an attribute "abstract" holding an iterable of method names')
    try:
        cls.abstract_names_only = {method_name_description_pattern.match(name).group(1) for name in abstract_method_descriptions}
    except AttributeError:
        raise TypeError('method name/description in attribute "abstract" invalid')
    cls.__bases__ += (_ABC,)
    cls.subclasses = set()
    return cls


def implementor(cls):
    """Decorator for inheritor class"""
    if _ABC not in cls.__bases__[0].__bases__:
        raise TypeError('@Implementor should be used on a subclass of a model decorated with @Interface')
    cls.__bases__[0].subclasses.add(cls.__name__)
    return cls
