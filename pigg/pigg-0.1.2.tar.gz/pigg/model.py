from abc import ABCMeta,abstractmethod


class Model(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.name = self.__class__.__name__

    def __call__(self, data):
        return self._predict(self._pre_process(data))

    @abstractmethod
    def _pre_process(self, data):
        pass

    @abstractmethod
    def _predict(self, processed_data):
        pass

