# -*- coding:utf-8 -*-
"""
@author:code37
@file:multi.py
@time:2018/4/1217:22
"""

from arctic import Arctic
from time import sleep
from time import time
from tushare.stock import cons as ct
from pandas.compat import StringIO
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import grequests
import requests
import pandas as pd
import multiprocessing as mp
import math
import sys
import re
import os



def all_symbol(lib):
    return lib.list_symbols()

def read_fundemental(lib, ticker):
    """

    :param lib: arctic.store.version_store.VersionStore
    :param ticker: 
    :return: 
    """
    # 去除字符，保留前六位编号
    ticker = re.sub(r'\D', '', ticker)
    return lib.read(ticker).data

def delete_none(lib):
    for i in lib.list_symbols():
        if len(read_fundemental(lib, i)) == 0:
            lib.delete(i)

def get_proxy():
    return requests.get("http://192.168.0.247:5010/get/").content

def get_all_proxy():
    return requests.get("http://192.168.0.247:5010/get_all/").json()

def delete_proxy(proxy):
    requests.get("http://192.168.0.247:5010/delete/?proxy={}".format(proxy))

def tryproxy(url):
    with requests.Session() as s:
        retries = Retry(total=2, backoff_factor=0.1,
                    status_forcelist=[500, 502, 503, 504],
                    raise_on_redirect=True, raise_on_status=True
                   )
        proxies = {"http": "http://{}".format(get_proxy().decode(encoding="utf-8", errors="strict"))}
        print('使用' + proxies.get('http', '')[7:])
        s.mount('http://', HTTPAdapter(max_retries=retries)) # 设置max_retries
        s.mount('https://', HTTPAdapter(max_retries=retries))
        headers={'User-Agent': UserAgent(verify_ssl=False).random,
                 'Host': 'money.finance.sina.com.cn',
                 'Referer': 'http://money.finance.sina.com.cn/',
                 'GET': url,
                 'Connection': 'close'}
        s.headers.update(headers)
        request = grequests.get(url, session=s, proxies=proxies, timeout=(2.5, 15))
        return request

# 协程处理tryproxy
def send_request(urls, size=2):
    rs = [tryproxy(url) for url in urls]
    res = grequests.imap(rs, stream=False, size=size, exception_handler = exception_handler)
    return [i for i in res]

# 清洗数据
def data_clean(r, symbol):
    text = r.text
    text = text.replace('\t\n', '\r\n')
    text = text.replace('\t', ',')
    df = pd.read_csv(StringIO(text), dtype={'code': 'object'})
    col = df.iloc[:,0].tolist()
    df = df.T
    df.rename(columns=df.iloc[0], inplace=True)
    df.drop(df.index[0], inplace=True)
    df.index = pd.to_datetime(df.index)
    df.index.name = 'date'
    return [symbol, df]
#     return df, col

# 写入数据
def write_to_MongoDB(lib, symbol, df, source='Tushare'):
    try:
        lib.write(symbol, df, metadata={'source': source})
        print(symbol + '写入完成')
    except Exception as e:
        print("Failed for ", str(e))

def balance_sheet_url(code):
    urls = [ct.SINA_BALANCESHEET_URL % i[0:6] for i in code if i[0:6].isdigit()]
    return urls

def profit_statement_url(code):
    urls = [ct.SINA_PROFITSTATEMENT_URL % i[0:6] for i in code if i[0:6].isdigit()]
    return urls

def cash_flow_url(code):
    urls = [ct.SINA_CASHFLOW_URL % i[0:6] for i in code if i[0:6].isdigit()]
    return urls

def exception_handler(request, exception):
    """
    操作错误
    """
    proxy = request.kwargs.get('proxies', {}).get('http', '')[7:]
    # delete_proxy(proxy)
    print('删除' + proxy)
    print('request url:{} failed'.format(request.url))
    print(exception)

# Some tools
def chunks(arr, m):
    n = int(math.ceil(len(arr) / float(m)))
    return [arr[i:i + n] for i in range(0, len(arr), n)]

def forfor(a):
    return [item for sublist in a for item in sublist]

def run(lib, urls, nums, processes=4):
    pool = mp.Pool(processes)
    urls = chunks(urls, len(urls) / nums) if int(len(urls) / nums) >= 1 else urls
    unseen = set(forfor(urls))
    seen = set()
    count = 1
    results = []
    while len(unseen) != 0:
        print('第' + str(count) + '次尝试！！！')
        print('剩余' + str(len(unseen)) + "个！！！")
        print('Crawl_jobs start!!!!!!!!')

        try:
            crawl_jobs = [pool.apply_async(send_request, args=(url,)) for url in urls]
            # print(crawl_jobs)
            responses_list = forfor([j.get() for j in crawl_jobs])
            # print(responses_list)
            sleep(0.1)
        except Exception as e:
            print(e)
            break

        seen.update(set(i.url for i in responses_list if i.status_code == requests.codes.ok))
        # print(seen)

        unseen = unseen - seen  # get new url to crawl
        print("还有", len(unseen), "没处理！")

        if len(unseen):
            # 剩下的部分nums个一组
            num = int(len(unseen)/nums) if int(len(unseen)/nums) >= 1 else 1
            urls = chunks(list(unseen), num)

        print('Parse_jobs start!!!!!!!!')
        parse_jobs = [pool.apply_async(data_clean, args=(r, r.url[len(r.url)-21:len(r.url)-15],)) for r in responses_list]
        try:
            results = [j.get() for j in parse_jobs]
        except Exception as e:
            print(e)

        if len(results):
            for l in results:
                symbol = l[0]
                df = l[1]
                print(symbol, type(df), len(df))

        print('Analysing and Writing!!!!!!!!')
        write_job = [pool.apply_async(write_to_MongoDB, args=(lib, l[0], l[1],)) for l in results]
        try:
            for j in write_job:
                 j.get()
        except Exception as e:
            print(e)

        count += 1
    pool.close()
    pool.join()

def main(lib, l, pkg_amount=40, nums=20, proxy_min=50):
    """
    
    :param lib: VersionStore
    :param l: url list
    :param pkg_amount: 将所有url分几个package生产task，一个package里有近pkg_amount个
    :param nums: 一个package里nums个为一组，供生成器map
    :param proxy_min: 
 
    :return: 
    """
    url_pkg = chunks(l, len(l) / pkg_amount)

    a = time()
    percent = 0.0

    while 1:
        for urls in url_pkg:
            if len(get_all_proxy()) > proxy_min:
                run(lib, urls, nums)
                percent += 100 / len(url_pkg)
                sleep(0.2)
            sys.stdout.write(('=' * int(percent)) + ('' * (100 - int(percent))) + ("\r [ %d" % percent + "% ] "))
            sys.stdout.flush()
        if percent == 100:
            sys.stdout.write('\n')
            sys.stdout.flush()
            break

    b = time() - a
    print(b)


if __name__ == '__main__':
    # mongod --dbpath D:/idwzx/project/arctic

    # cd C:\Program Files\Redis
    # redis-server.exe redis.windows.conf

    a = Arctic('localhost')
    # 删除library
    # a.delete_library('ashare_BS')
    a.initialize_library('ashare_BBS')
    lib = a['ashare_BBS']

    # 股票列表
    allAshare = pd.read_csv(os.path.abspath('./allAShare.csv'))
    allAshare = allAshare['0']

    tickers = set([re.sub(r'\D', '', i) for i in allAshare]) - set(lib.list_symbols())
    l = balance_sheet_url(list(tickers))
    # l = balance_sheet_url(allAshare[1000:len(allAshare)].tolist())
    main(lib, l, pkg_amount=100, nums=20, proxy_min=110)