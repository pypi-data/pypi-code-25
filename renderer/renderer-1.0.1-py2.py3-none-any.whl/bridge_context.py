import sys
import abc
from renderer.ver2 import VersionTwoRenderer, VersionTwoImplementor
from renderer.ver3 import VersionThreeRenderer, VersionThreeImplementor


class Context(object):
    def __init__(self, ):
        super(Context, self).__init__()

    def render(self, data='', target='file'):
        renderer = RendererCreator(target=target).product
        r = renderer.render(data)
        return r


"""
Define an interface for creating an object, but let subclasses decide
which class to instantiate. Factory Method lets a class defer
instantiation to subclasses.
"""


class Creator(object):
    """
    Declare the factory method, which returns an object of type Product.
    Creator may also define a default implementation of the factory
    method that returns a default ConcreteProduct object.
    Call the factory method to create a Product object.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        self._product = self._factory_method(**kwargs)

    @abc.abstractmethod
    def _factory_method(self, **kwargs):
        pass

    @property
    def product(self):
        return self._product
        pass


class RendererCreator(Creator):
    """
    Override the factory method to return an instance of a
    ConcreteProduct1.
    """

    def _factory_method(self, **kwargs):
        """

        :rtype: [VersionTwoRenderer ,VersionThreeRenderer]
        """
        imp = ImplementerCreator().product
        if sys.version_info.major == 2:
            return VersionTwoRenderer(target=kwargs.get('target', 'file'), imp=imp)
        else:
            return VersionThreeRenderer(target=kwargs.get('target', 'file'), imp=imp)
        pass


class ImplementerCreator(Creator):
    """
    Override the factory method to return an instance of a
    ConcreteProduct2.
    """

    def _factory_method(self, **kwargs):
        if sys.version_info.major == 2:
            return VersionTwoImplementor()
        else:
            return VersionThreeImplementor()
        pass
