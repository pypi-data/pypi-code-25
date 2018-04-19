# -*- coding:utf-8 -*-
"""
@author:code37
@file:Data_reader.py
@time:2018/4/1816:55
"""

from arctic import Arctic
import pandas as pd
import re

def all_symbol(lib):
    return lib.list_symbols()

def read_stock(lib, ticker):
    """
    :param lib: arctic.store.version_store.VersionStore
    :param ticker: 
    :return: 
    """

    return lib.read(ticker).data

def read_fund(lib, ticker):
    """

    :param lib: arctic.store.version_store.VersionStore
    :param ticker: 
    :return: 
    """
    # 去除字符，保留前六位编号
    ticker = re.sub(r'\D', '', ticker)
    return lib.read(ticker).data

def concat_all_data(lib, date_range=None):
    return pd.concat([pd.DataFrame(lib.read(s, date_range=date_range).data) for s in lib.list_symbols()])

if __name__ == '__main__':
    a = Arctic('localhost')
    a.initialize_library('ashare_BS')
    lib = a['ashare_BS']
    print(all_symbol(lib), len(all_symbol(lib)))