# -*- coding:utf-8 -*-
"""
@author:code37
@file:item.py
@time:2018/3/279:20
"""
from arctic import Arctic
from time import sleep
import math
import tushare as ts
import alphafactory.Tufund as tf
import pandas as pd
import re
import os


def write_all_stock(allAshare, lib):
    """
    :param allAshare: List，所有股票
    :param lib: arctic.store.version_store.VersionStore
    
    :return: succ: List, written stocks; fail: List, failed written stocks  
    """
    succ = []
    fail = []
    cons = ts.get_apis()
    for symbol in allAshare:
        try:
            item = ts.bar(symbol, cons, freq='D', start_date='', end_date='').sort_index(ascending=True)
            lib.write(symbol, item, metadata={'source': 'Tushare'})
            print(symbol + '写入完成')
            succ.append(symbol)
        except Exception as e:
            fail.append(symbol)
            print("Failed for ", symbol, str(e))
        sleep(0.1)
    return succ, fail


if __name__ == '__main__':
    # mongod --dbpath D:/idwzx/project/arctic
    a = Arctic('localhost')
    a.initialize_library('ashare_BS')
    lib = a['ashare_BS']
    allAshare = pd.read_csv(os.path.abspath('./allAShare.csv'))
    allAshare = allAshare['0']

    succ_list, fail_list = write_all_stock(allAshare, lib)

    with open(os.path.abspath('./succ_list.txt'), 'w') as f:
        f.write(str(succ_list))
    with open(os.path.abspath('./fail_list.txt'), 'w') as f:
        f.write(str(fail_list))


