from .stock import Stock

class PyIEX(object):

    def __init__(self):
        self._stock = Stock()

    @property
    def stock(self):
        return self._stock
