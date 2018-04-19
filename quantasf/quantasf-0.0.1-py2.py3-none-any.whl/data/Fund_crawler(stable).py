# -*- coding:utf-8 -*-
"""
@author:code37
@file:crawler_stable.py
@time:2018/4/1815:20
"""
import asyncio
import aiohttp
import async_timeout
import pandas as pd
from pandas.compat import StringIO
from tushare.stock import cons as ct
from arctic import Arctic
import time
import os

############ SETTING #############

TYPE = 'BS' # 'IS', 'CF'
MONGO = True
CSV = True

############ CHANGE ABOVE SETTING #############

if MONGO:
    # mongod --dbpath D:/idwzx/project/arctic
    a = Arctic('localhost')
    a.initialize_library('ashare_{}'.format(TYPE))
    lib = a['ashare_{}'.format(TYPE)]

result_dict = {}

allAshare = pd.read_csv(os.path.abspath('./allAShare.csv'))
allAshare = allAshare['0']

def balance_sheet_url(code):
    url = ct.SINA_BALANCESHEET_URL % code[0:6]
    return url

def profit_statement_url(code):
    url = ct.SINA_PROFITSTATEMENT_URL % code[0:6]
    return url

def cash_flow_url(code):
    url = ct.SINA_CASHFLOW_URL % code[0:6]
    return url

async def get_proxy():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://192.168.0.247:5010/get/") as response:
            proxy_str = await response.text()
            return "http://{}".format(proxy_str)

async def fetch(queue, session, url):
    proxy_url = await get_proxy()
    print('proxy: ' + proxy_url)
    ticker = url.split('/')[-3]
    try:
        async with async_timeout.timeout(5):
            async with session.get(url, proxy=proxy_url, allow_redirects=True) as resp:
                if resp.status == 200 or 201:
                    return await resp.text()
                else:
                    await queue.put(ticker)
    except Exception as e:
        print(e)
        print('Put {} in queue!'.format(ticker))
        await queue.put(ticker)

async def consume(queue):
    while True:
        ticker = await queue.get()
        async with aiohttp.ClientSession() as session:
            if TYPE == 'BS':
                target_url = balance_sheet_url(ticker)
            elif TYPE == 'IS':
                target_url = profit_statement_url(ticker)
            elif TYPE == 'CF':
                target_url = cash_flow_url(ticker)
            else:
                raise Exception
            html = await fetch(queue, session, target_url)
            result_dict[ticker] = html
        queue.task_done()

async def run(queue, max_tasks):
    # schedule the consumer
    tasks = [asyncio.ensure_future(consume(queue)) for _ in range(max_tasks)]
    await queue.join()
    for w in tasks:
        w.cancel()

def write_to_MongoDB(lib, symbol, df, source='Tushare'):
    try:
        lib.write(symbol, df, metadata={'source': source})
        print(symbol + '写入完成')
    except Exception as e:
        print("Failed for ", str(e))


def data_clean(text):
    text = text.replace('\t\n', '\r\n')
    text = text.replace('\t', ',')
    df = pd.read_csv(StringIO(text), dtype={'code': 'object'})
    df = df.T
    df.rename(columns=df.iloc[0], inplace=True)
    df.drop(df.index[0], inplace=True)
    df.index = pd.to_datetime(df.index)
    df.index.name = 'date'
    return df

def main(num=10):
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue(loop=loop)
    for ticker in allAshare:
        queue.put_nowait(ticker)
    print(queue)
    loop.run_until_complete(run(queue, num))
    loop.close()

    fail = []
    for key in result_dict:
        try:
            df = data_clean(result_dict[key])
            if MONGO:
                write_to_MongoDB(lib, key, df)
            print("{0}写入{1}条数据,".format(key, len(df)))
        except ValueError as e:
            fail.append(key)
            print("{}写入失败".format(key))
    print("{}爬取失败".format(fail))
    if CSV:
        pd.DataFrame(result_dict).to_csv(os.path.abspath("./allAshare{}.csv".format(TYPE)))

if __name__ == '__main__':
    start = time.time()
    main(num=20)
    print(time.time()-start)

