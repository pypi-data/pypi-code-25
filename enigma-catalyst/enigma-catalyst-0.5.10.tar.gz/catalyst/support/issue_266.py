import pytz
from datetime import datetime, timedelta
from catalyst.api import symbol
from catalyst.utils.run_algo import run_algorithm

coin = 'btc'
base_currency = 'usd'
n_candles = 5


def initialize(context):
    context.symbol = symbol('%s_%s' % (coin, base_currency))


def handle_data_polo_partial_candles(context, data):
    # all I do is print the current last 2 candles (5T)
    history = data.history(symbol('btc_usd'), ['volume'],
                           bar_count=1,
                           frequency='5T')

    current = data.current(symbol('btc_usd'), ['price'])

    print('\nnow: %s\n%s' % (data.current_dt, history))
    if not hasattr(context, 'i'):
        context.i = 0
    context.i += 1
    if context.i > 5:
        raise Exception('stop')


live = True
if live:
    run_algorithm(initialize=lambda ctx: True,
                  handle_data=handle_data_polo_partial_candles,
                  exchange_name='kraken',
                  base_currency='usdt',
                  algo_namespace='ns',
                  live=True,
                  data_frequency='daily',
                  capital_base=3000,
                  #start=datetime(2018, 2, 2, 0, 0, 0, 0, pytz.utc),
                  #end=datetime(2018, 2, 20, 0, 0, 0, 0, pytz.utc)
                )
else:
    run_algorithm(initialize=lambda ctx: True,
                  handle_data=handle_data_polo_partial_candles,
                  exchange_name='binance',
                  base_currency='usdt',
                  algo_namespace='ns',
                  live=False,
                  data_frequency='minute',
                  capital_base=3000,
                  start=datetime(2018, 4, 5, 0, 0, 0, 0, pytz.utc),
                  end=datetime(2018, 4, 7, 0, 0, 0, 0, pytz.utc))

