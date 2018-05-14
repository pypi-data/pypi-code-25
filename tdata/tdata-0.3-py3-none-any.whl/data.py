# version 1.0
# replace update
# TODO: append update

import pandas as pd
from sqlalchemy import create_engine

from zen.quantos import ds

engine = create_engine('sqlite:///data/history.db')

# get index and stocks list
index_df, msg = ds.query(
    view='jz.instrumentInfo',
    fields='status,list_date,fullname_en,market',
    filter='inst_type=100&status=1&symbol=',
    data_format='pandas')
stock_df, msg = ds.query(
    view='jz.instrumentInfo',
    fields='status,list_date,fullname_en,market',
    filter='inst_type=1&status=1&symbol=',
    data_format='pandas')

indexes = ','.join(index_df.loc[:, 'symbol'])
stocks = ','.join(stock_df.loc[:, 'symbol'])

# get daily history
df, msg = ds.daily(
    indexes,
    start_date=20100101,
    end_date=20180316,
    fields=
    'symbol,close,freq,high,low,open,trade_date,trade_status,turnover,volume')

# TODO
# end_date = last trade date
# write to database
