import requests

from .utils import API
from .utils.func_utils import ensure_params_under_instance_context


class Stock(API):

    def __init__(self, symbol, **preferences):
        super(Stock, self).__init__('Stock', '1.0', 'stock')
        self._preferences = preferences
        self.symbol = symbol

    @classmethod
    def symbols(cls):
        url = 'https://api.iextrading.com/1.0/ref-data/symbols'
        return requests.get(url).json()

    def batch_request(self, types, symbols=None, range=None, **kwargs):
        raise NotImplementedError

    @ensure_params_under_instance_context
    def book(self, symbol):
        return self._call(['{symbol}', 'book'], symbol=symbol)

    @ensure_params_under_instance_context
    def chart(self, symbol, range=range):
        """
        Chart API
        does not support date range
        """
        return self._call(['{symbol}', 'chart', '{range}'],
                          symbol=symbol, range=range)

    @ensure_params_under_instance_context
    def company(self, symbol):
        """
        Company API
        """
        return self._call(['{symbol}', 'company'], symbol=symbol)

    @ensure_params_under_instance_context
    def delayed_quote(self, symbol):
        return self._call(['{symbol}', 'delayed-quote'], symbol=symbol)

    @ensure_params_under_instance_context
    def dividends(self, symbol, range):
        return self._call(['{symbol}', 'dividends', '{range}'],
                          symbol=symbol, range=range)

    @ensure_params_under_instance_context
    def earnings(self, symbol):
        return self._call(['{symbol}', 'earnings'], symbol=symbol)

    @ensure_params_under_instance_context
    def financials(self, symbol):
        return self._call(['{symbol}', 'financials'], symbol=symbol)

    @ensure_params_under_instance_context
    def stats(self, symbol):
        return self._call(['{symbol}', 'stats'], symbol=symbol)

    @ensure_params_under_instance_context
    def news(self, symbol, range=None):
        if range is None:
            return self._call(['{symbol}', 'news'], symbol=symbol)
        else:
            return self._call(['{symbol}', 'news', 'last', '{range}'],
                              symbol=symbol, range=range)

    @ensure_params_under_instance_context
    def peers(self, symbol):
        return self._call(['{symbol}', 'peers'], symbol=symbol)

    @ensure_params_under_instance_context
    def quote(self, symbol, **kwargs):
        return self._call(['{symbol}', 'quote'], symbol=symbol, **kwargs)

    @ensure_params_under_instance_context
    def splits(self, symbol, range=None):
        if range is None:
            return self._call(['{symbol}', 'splits'], symbol=symbol)
        else:
            return self._call(['{symbol}', 'splits', '{range}'],
                              symbol=symbol, range=range)


if __name__ == '__main__':
    print(Stock.symbols())
    apple = Stock('aapl')
    print(apple.book())
    print(apple.chart(range='5y'))
    print(apple.company())
    print(apple.delayed_quote())
    print(apple.dividends(range='5y'))
    print(apple.earnings())
    print(apple.financials())
    print(apple.stats())
    print(apple.news())
    print(apple.peers())
    print(apple.quote())
    print(apple.splits())
