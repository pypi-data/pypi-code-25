import ccxt
import datetime
import pytz
import re


def convert_dt_to_ts(dt):
    #timezone = datetime.timezone.utc
    timezone = pytz.utc
    #dt = dt.replace(tzinfo=timezone).timestamp() * 1000
    epoch_start = timezone.localize(datetime.datetime(1970, 1, 1))
    ts = (timezone.localize(dt) - epoch_start).total_seconds() * 1000

    return ts


def compare_timestamps(data, timeframe):
    granularity = convert_timeframe(timeframe)
    last_ts = datetime.datetime.utcfromtimestamp(data)
    now = datetime.datetime.utcnow()
    rounded_now = return_rounded_time(now, granularity)

    if last_ts == rounded_now:
        match = True

    else:
        match = False

    return match


def convert_timeframe(timeframe):
    timeframe_dict = {'1m': 60, '5m': 300, '15m': 900, '30m': 1800, '1h': 3600, '2h': 7200, '4h': 14400, '6h': 21600,
                      '8h': 28800, '12h': 43200, '1d': 86400, '3d': 259200, '1w': 604800, '1M': 2592000}
    granularity = timeframe_dict[timeframe]

    return granularity


def create_connection(exchange_id, settings, authenticated=False, dev_mode=False):
    exchange_method = getattr(ccxt, exchange_id)
    exchange = exchange_method()
    exchange.enableRateLimit = True

    if authenticated:
        exchange.apiKey = settings['apiKey']
        exchange.secret = settings['secret']

        if 'password' in settings:
            exchange.password = settings['password']

        if 'uid' in settings:
            exchange.uid = settings['uid']

    if dev_mode:
        exchange.urls['api'] = exchange.urls['test']
        exchange.verbose = True

    try:
        exchange.load_markets()

    except ccxt.ExchangeNotAvailable:
        raise Exception('Failed to connect to {} because it is not currently available.'.format(exchange_id))

    except ccxt.NotSupported:
        raise Exception('Request to connect to {} failed because the endpoint is not supported.'.format(exchange.name))

    except ccxt.AuthenticationError:
        raise Exception('Failed to authenticate connection to {} because of an error in one or more API credentials.'.
                        format(exchange_id))

    except ccxt.InvalidNonce:
        raise Exception('Failed to authenticate connection to {} because the nonce is invalid.'.format(exchange_id))

    return exchange


def create_symbols_list(exchange, quote):
    symbols_list = []

    for symbol in exchange.symbols:
        symbol_quote = re.split('/', symbol)[1]

        if quote == symbol_quote:
            symbols_list.append(str(symbol))

    return symbols_list


def create_uohlcv_dict(data, symbol, timeframe):
    close_price = float(data[4])
    high_price = float(data[2])
    low_price = float(data[3])
    open_price = float(data[1])
    utc_timestamp = datetime.datetime.utcfromtimestamp(data[0] // 1000)
    volume = float(data[5])
    uohlcv_dict = {'close': close_price, 'high': high_price, 'low': low_price, 'open': open_price,
                   'symbol': symbol, 'timeframe': timeframe, 'utc_timestamp': utc_timestamp,
                   'volume': volume}

    return uohlcv_dict


def fund_account(amount, currency, destination, exchange, type, params=None):
    funding_type = getattr(exchange, type)

    try:
        funding = funding_type(currency, amount, destination, params=params)

    except ccxt.ExchangeNotAvailable:
        data = {'result': 'error',
                'message': '{} request for {} in {} on {} has failed due to a 403: Forbidden for Client error.'.
                    format(type, amount, currency, exchange.name)}

    except ccxt.InsufficientFunds:
        data = {'result': 'error',
                'message': '{} request for {} in {} on {} has failed due to insufficient funds.'.
                    format(type, amount, currency, exchange.name)}

    else:
        data = {'result': 'info',
                'message': '{} request for {} in {} on {} has succeeded with ID {}'.
                    format(type, amount, currency, exchange.name, funding['id'])}

    return data


def get_candlestick_data(exchange, limit, symbol, timeframe, since=None, test_match=True):
    try:
        candlesticks = exchange.fetch_ohlcv(symbol, limit=limit, since=since, timeframe=timeframe)

    except ccxt.DDoSProtection:
        data = {'result': 'error',
                'message': 'Request to get OHLV data from {} failed because the data rate limit has been exceeded.'
                    .format(exchange.name)}

    except ccxt.RequestTimeout:
        data = {'result': 'error',
                'message': 'Request to get OHLV data from {} failed on a time out.'.format(exchange.name)}

    else:
        if (test_match and compare_timestamps(candlesticks[0][0] / 1000, timeframe)) or (not test_match):
            data_dict = create_uohlcv_dict(candlesticks[0], symbol, timeframe)
            data = {'result': 'info', 'message': data_dict}

        else:
            message = 'Requested and returned timestamps did not match.'
            data = {'result': 'error', 'message': message}

    return data


def get_usd_balance(exchange):
    balance = [float(balance['available']) for balance in exchange.fetch_balance()['info']
               if balance['currency'] == 'USD'][0]

    return balance


def return_rounded_time(ts, granularity):
    seconds = (ts - ts.min).seconds
    rounding = seconds // granularity * granularity
    rounded_down_time = ts + datetime.timedelta(0, rounding - seconds, -ts.microsecond)

    return rounded_down_time


def update_order(exchange, id):
    order = exchange.fetch_order(id)['info']

    return order