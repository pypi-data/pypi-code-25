# -*- coding:utf-8 -*- 

SERVER = '118.112.186.15'
PORT = 6888
URL = 'http://%s:%s/api/v1/%s'

GET_INDEX = 'GetIndex/%s'

GET_INDEXDATA = 'IndexData/'

GET_HISTORY_BYLENGTH = 'IndexHistory/%s/%s'

GET_INDEXES = 'Indexes/%s'

GET_INDEX_COINS = 'ListIndexCoins/%s'

INDEX_COLS = ['name', 'fullname', 'create_dt', 'type', 'value', 'value_usd', 'percent_change_24h', 'timestamp', 
                     'description', 'description_cn']

HISTORY_COLS = ['date', 'btc_index', 'usdt_index']
MSG_FOR_INPUT = '请至少输入参数index_name'
