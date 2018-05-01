from abc import ABCMeta, abstractmethod


class DriverBase(object):
    __metaclass__ = ABCMeta

    @classmethod
    def get_name(cls):
        return getattr(cls, 'name', cls.__name__)

    def match(self, url):
        return self._match(url)

    @abstractmethod
    def _match(self, url):
        raise NotImplementedError()
