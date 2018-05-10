import da_ponz.utilities.api_tools as api_tools
import da_ponz.strategies.common_functions as common_functions
import da_ponz.utilities.logging_tools as logging_tools
import da_ponz.utilities.sql_tools as sql_tools
import da_ponz.utilities.settings_tools as settings_tools
import datetime
import itertools
import math
import sys
import time


def calculate_request_loops(granularity, limit, test_start_ts):
    adj_now = api_tools.return_rounded_time(datetime.datetime.utcnow(), granularity)
    request_loops = int(math.ceil((adj_now - test_start_ts).total_seconds() / (granularity * limit)))

    return request_loops


def calculate_test_start_ts(engine, granularity, setting):
    results = common_functions.get_test_data(['utc_timestamp'], engine, granularity, 'BTC/USD', limit=1)

    if not results:
        test_start_ts = datetime.datetime.strptime(setting, '%Y-%m-%d %H:%M:%S')

    else:
        test_start_ts = results[0][0] + datetime.timedelta(seconds=granularity)

    return test_start_ts


settings = settings_tools.load_settings(sys.argv[1])
exchange_id = 'gdax'
api_settings = settings['api'][exchange_id]
exchange = api_tools.create_connection(exchange_id, api_settings, authenticated=True)
engine = sql_tools.create_engine(settings['mysql_connection'])
logger = logging_tools.create_logger(sys.argv[2])
limit = settings['api'][exchange_id]['limit']
timezone = datetime.timezone.utc
markets = exchange.load_markets()
symbols_list = [symbol for symbol in markets if 'USD' in symbol]
timeframes_list = settings['api'][exchange_id]['timeframes']

for item in itertools.product(symbols_list, timeframes_list):
    symbol = item[0]
    timeframe = item[1]
    granularity = exchange.timeframes[timeframe]
    message = 'Getting data for the symbol {} at the {} seconds granularity...'.format(symbol, granularity)
    logging_tools.log_event('info', logger, message)

    test_start_ts = calculate_test_start_ts(engine, granularity, settings['api'][exchange_id]['test_start'])
    request_loops = calculate_request_loops(granularity, limit, test_start_ts)

    message = 'Running through {} loop(s) to obtain the requested amount of data...'.format(request_loops)
    logging_tools.log_event('info', logger, message)

    for i in range(request_loops):
        since = test_start_ts + datetime.timedelta(seconds=granularity * limit * i)
        since = since.replace(tzinfo=timezone).timestamp() * 1000
        data = api_tools.get_candlestick_data(exchange, limit, symbol, timeframe, since=since, test_match=False)

        for i in range(1, 15):
            if data['result'] == 'info':
                table = sql_tools.get_table(engine, 'testing_data')
                logging_tools.log_event(data['result'], logger, data['message'])
                #insert = sql_tools.insert_data(engine, table, data['message'])
                #logging_tools.log_event(insert['result'], logger, insert['message'])

                break

            else:
                logging_tools.log_event(data['result'], logger, data['message'])
                delay = 60
                message = 'Trying again in {} seconds. This is attempt {} of 15.'.format(delay, i)
                logging_tools.log_event('error', logger, message)
                time.sleep(delay)