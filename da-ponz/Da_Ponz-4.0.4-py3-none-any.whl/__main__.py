import da_ponz.utilities.api_tools as api_tools
import da_ponz.utilities.logging_tools as logging_tools
import da_ponz.utilities.settings_tools as settings_tools
import da_ponz.utilities.sql_tools as sql_tools
import da_ponz.strategies.testing as strat_testing
import datetime
import sys
from tendo import singleton
import time


da_ponz = singleton.SingleInstance()

exchange_id = 'gdax'
logger = logging_tools.create_logger(sys.argv[2])
settings = settings_tools.load_settings(sys.argv[1])
api_settings = settings['api'][exchange_id]
engine = sql_tools.create_engine(settings['mysql_connection'])
'''exchange = api_tools.create_connection(exchange_id, api_settings, authenticated=True, dev_mode=True)
balance = api_tools.get_usd_balance(exchange)

if balance < 1:
    data = order_tools.fund_account(10000, 'USD', exchange, api_settings, 'deposit')
    logging_tools.log_event(data['result'], logger, data['message'])

order_tests = [{'price': None, 'side': 'buy', 'type': 'market'}, {'price': None, 'side': 'sell', 'type': 'market'},
               {'price': 850, 'side': 'buy', 'type': 'limit'}]

for test in order_tests:
    data = order_tools.submit_order(2, exchange, test['side'], 'ETH/USD', test['type'], price=test['price'])
    logging_tools.log_event(data['result'], logger, data['message']['order'])
    table = sql_tools.get_table(engine, data['message']['table'])
    insert = sql_tools.insert_data(engine, table, data['message']['order'])
    logging_tools.log_event(insert['result'], logger, insert['message'])'''

exchange = api_tools.create_connection(exchange_id, api_settings)
'''symbols_list = api_tools.create_symbols_list(exchange, 'USD')

for symbol in symbols_list:
    now = datetime.datetime.utcnow()
    timeframe = settings['da_ponz']['timeframe']

    for i in range(1, 15):
        data = api_tools.get_candlestick_data(exchange, 30, symbol, timeframe)

        if data['result'] == 'info':
            table = sql_tools.get_table(engine, 'market_data')
            logging_tools.log_event(data['result'], logger, data['message'])
            insert = sql_tools.insert_data(engine, table, data['message'])
            logging_tools.log_event(insert['result'], logger, insert['message'])

            break

        else:
            logging_tools.log_event(data['result'], logger, data['message'])
            delay = 60
            message = 'Trying again in {} seconds. This is attempt {} of 15.'.format(delay, i)
            logging_tools.log_event('error', logger, message)
            time.sleep(delay)'''

#strat_testing.setup_testing(engine, exchange, logger)
table = sql_tools.get_table(engine, logger, 'testing_data')
