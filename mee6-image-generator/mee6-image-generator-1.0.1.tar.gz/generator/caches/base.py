import abc


class SVGCache:
    @abc.abstractmethod
    def get(self, parameters):
        pass

    @abc.abstractmethod
    def add(self, parameters, png_bytes):
        pass
