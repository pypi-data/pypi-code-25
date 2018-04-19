# -*- coding:utf-8 -*-
"""
@author:code37
@file:test.py
@time:2018/3/279:20
"""

from arctic import CHUNK_STORE, Arctic
from time import sleep
import tushare as ts
import pandas as pd
import os


def write_all_stock(allAshare):
    succ = []
    fail = []
    cons = ts.get_apis()
    for symbol in allAshare:
        try:
            item = ts.bar(symbol, cons, freq='D', start_date='', end_date='').sort_index(ascending=True)
            item.index.rename('date', inplace=True)
            lib.write(symbol, item, chunk_size='D')
            succ.append(symbol)
            print(symbol + '写入完成')
        except Exception as e:
            fail.append(symbol)
            print("Failed for ", symbol, str(e))
        sleep(0.1)
    return succ, fail

if __name__ == '__main__':
    # mongod --dbpath D:/idwzx/project/chunk --port 1234
    a = Arctic('localhost:1234')
    a.initialize_library('Achunk', lib_type=CHUNK_STORE)
    lib = a['Achunk']
    allAshare = pd.read_csv(os.path.abspath('./allAShare.csv'))
    allAshare = allAshare['0']

    succ_list, fail_list = write_all_stock(allAshare)
    with open('D:/idwzx/project/alphafactory/succ_list.txt', 'w') as f:
        f.write(str(succ_list))
    with open('D:/idwzx/project/alphafactory/fail_list.txt', 'w') as f:
        f.write(str(fail_list))

