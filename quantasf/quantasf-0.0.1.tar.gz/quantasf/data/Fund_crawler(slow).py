# -*- coding:utf-8 -*-
"""
@author:code37
@file:item.py
@time:2018/3/279:20
"""

from arctic import Arctic
from time import sleep
from tushare.stock import cons as ct
from pandas.compat import StringIO
from fake_useragent import UserAgent
import requests
import pandas as pd
import os

def get_proxy():
    return requests.get("http://192.168.0.247:5010/get/").text()

def get_all_proxy():
    return requests.get("http://192.168.0.247:5010/get_all/").json()

def delete_proxy(proxy):
    requests.get("http://192.168.0.247:5010/delete/?proxy={}".format(proxy))

def tryproxy(url):
    """
    每个proxy试5次直到试出能用的返回
    :param url: 
    :return: df
    """
    while True:
        retry_count = 2
        proxy = get_all_proxy()[0]
        print('使用' + proxy)
        while retry_count:
            try:
                # 使用代理访问
                request = requests.get(url,
                                       headers={'User-Agent': UserAgent().random,
                                                'Host': 'money.finance.sina.com.cn',
                                                'Referer': 'http://money.finance.sina.com.cn/',
                                                'GET': url},
                                       proxies={"http": "http://{}".format(proxy)},
                                       timeout = 1)
                text = request.text()
                text = text.replace('\t\n', '\r\n')
                text = text.replace('\t', ',')
                df = pd.read_csv(StringIO(text), dtype={'code': 'object'})
                return df
            except Exception:
                print(proxy + '尝试重连最后' + str(retry_count) + '次')
                retry_count -= 1
        else:
            delete_proxy(proxy)
            print('删除' + proxy)


def get_balance_sheet(code):
    """
        获取某股票的历史所有时期资产负债表
    Parameters
    --------
    code:str 股票代码 e.g:600518

    Return
    --------
    DataFrame
        行列名称为中文且数目较多，建议获取数据后保存到本地查看
    """
    if code.isdigit():
        url = ct.SINA_BALANCESHEET_URL % (code)
        df = tryproxy(url)
        return df


def get_profit_statement(code):
    """
        获取某股票的历史所有时期利润表
    Parameters
    --------
    code:str 股票代码 e.g:600518

    Return
    --------
    DataFrame
        行列名称为中文且数目较多，建议获取数据后保存到本地查看
    """
    if code.isdigit():
        url = ct.SINA_PROFITSTATEMENT_URL % (code)
        df = tryproxy(url)
        return df


def get_cash_flow(code):
    """
        获取某股票的历史所有时期现金流表
    Parameters
    --------
    code:str 股票代码 e.g:600518

    Return
    --------
    DataFrame
        行列名称为中文且数目较多，建议获取数据后保存到本地查看
    """
    if code.isdigit():
        url = ct.SINA_CASHFLOW_URL % (code)
        df = tryproxy(url)
        return df


def write_fundemental(allAshare, lib, ftype, source='Tushare', fund_dict=(False, 'D:/fund_dict.txt')):
    """

    :param allAshare: 
    :param lib: 
    :param type: 
    :param source: 
    :param fund_dict: 
    :return: 
    """
    succ = []
    fail = []
    col = []
    count = 0
    global headers

    for symbol in allAshare:
        try:
            if ftype == 'BS':
                item = get_balance_sheet(symbol[0:6])
            elif ftype == 'IS':
                item = get_profit_statement(symbol[0:6])
            elif ftype == 'CF':
                item = get_cash_flow(symbol[0:6])
            else:
                raise NameError("没有你要的表哦！")

            col.append(item.iloc[:,0].tolist())
            item = item.T
            item.rename(columns=item.iloc[0], inplace=True)
            item.drop(item.index[0], inplace=True)
            item.index = pd.to_datetime(item.index)
            item.index.name = 'date'
            lib.write(symbol, item.sort_index(ascending=True), metadata={'source': source})
            print(symbol + '写入完成')
            succ.append(symbol)
        except Exception as e:
            print("Failed for ", symbol, str(e))
            fail.append(symbol)
        count += 1

        sleep(0.1)

    col = list(set(col))

    if fund_dict[0]:
        with open(fund_dict[1], 'w') as f:
            f.write(str(col))

    return col, succ, fail

if __name__ == '__main__':
    # mongod --dbpath D:/idwzx/project/arctic
    a = Arctic('localhost')
    a.initialize_library('ashare_BS')
    lib = a['ashare_BS']
    allAshare = pd.read_csv(os.path.abspath('./allAShare.csv'))
    allAshare = allAshare['0']

    col, succ, fail = write_fundemental(allAshare, lib, 'BS')