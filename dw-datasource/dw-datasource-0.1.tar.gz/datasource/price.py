import pandas as pd
from tiingo import TiingoClient
from .util import retry

tiingo_client = TiingoClient()  # API key must be set in environment variable


def __get_historical(symbol, start=None, end=None, frequency='daily'):
    def map_data(data):
        """
        Map data to a new dict which uses adjusted data.
        """
        return {
            'open': data['adjOpen'],
            'high': data['adjHigh'],
            'low': data['adjLow'],
            'close': data['adjClose'],
            'volume': data['volume']
        }

    prices = tiingo_client.get_ticker_price(symbol,
                                            startDate=start,
                                            endDate=end,
                                            frequency=frequency,
                                            fmt='json')

    datetime_index = pd.DatetimeIndex([d['date'] for d in prices])
    data = map(map_data, prices)

    return pd.DataFrame(data=data, index=datetime_index)


def get_historical(symbol, start=None, end=None, frequency='daily'):
    """
    Get historical price data from tiingo as a dataframe.

    :param str symbol: symbol code
    :param str start: date string specifies the beginning of historical, e.g. 2018-1-1. If None then get latest data.
    :param str end: date string specifies the end of historical, e.g. 2018-5-1. If None then get latest data.
    :param str frequency: Data point frequency. Could be 'daily' 'weekly' 'monthly'

    :return: OHLC Dataframe
    """
    return retry(__get_historical)(symbol, start, end, frequency)
