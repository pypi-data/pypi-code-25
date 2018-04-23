from . import session

BASE_URL = 'https://api.lionshare.capital/api/'

class Lionshare(object):
    """Wrapper for Lionshare API
    
    Can get prices and market info of various cryptocurrencies
    """

    def __init__(self):
        self.base = BASE_URL + '{endpoint}{query}'

    def _get(self, endpoint, query=''):
        """Gets data from Lionshare API

        Keyword arguments:
        endpoint -- endpoint for HTTP API request
        query -- optional query string
        """
        url = self.base.format(endpoint=endpoint, query=query)
        response = session.get(url)
        return response.json()

    def get_prices(self, period=''):
        """Gets prices for cryptocurrencies

        Keyword arguments:
        period -- period to get historic prices (hour, day, week, month, year)

        If given period is not one of the five, data for week is returned
        """
        return self._get('prices', '?period=' + period)

    def get_markets(self):
        """Gets market info for cryptocurrencies"""
        return self._get('markets')