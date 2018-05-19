import quandl
import os
import pandas as pd
from .util import retry

QUANDL_TOKEN_ENVIRON = 'QUANDL_TOKEN'


def __get_us_treasury_yield(start, end, maturity):
    if QUANDL_TOKEN_ENVIRON not in os.environ:
        raise RuntimeError("Quandl token is not set. Put it into environ %s" % QUANDL_TOKEN_ENVIRON)
    quandl_token = os.environ[QUANDL_TOKEN_ENVIRON]
    data = quandl.get("USTREASURY/YIELD", authtoken=quandl_token)

    def map_columns(df):
        result = df.copy()
        result['1m'] = result['1 MO']
        result['3m'] = result['3 MO']
        result['6m'] = result['6 MO']
        result['1y'] = result['1 YR']
        result['2y'] = result['2 YR']
        result['3y'] = result['3 YR']
        result['5y'] = result['5 YR']
        result['7y'] = result['7 YR']
        result['10y'] = result['10 YR']
        result['20y'] = result['20 YR']
        result['30y'] = result['30 YR']
        return result

    data = map_columns(data)
    return data.loc[start:end, maturity]

def get_us_treasury_yield(start, end, maturity='10y'):
    """
    Get US treasury yield data.
    
    Arguments:
        start {[string]} -- Start date in string, e.g 2018-2-1
        end {[string]} -- End data in string, e.g 2018-5-11
    
    Keyword Arguments:
        maturity {str} -- [Maturity e.g 1m, 3m, 1y, 10y] (default: {'10y'})
    
    Returns:
        [type] -- [description]
    """

    return retry(__get_us_treasury_yield)(start, end, maturity)
