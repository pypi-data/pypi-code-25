#!/usr/bin/env python3
# -*- coding: utf-8 -*- #

import re
import os
import time
import argparse
import requests


"""
http://mis.twse.com.tw API list
getChartOhlcStatis
getDailyRangeOnlyKD
getDailyRangeWithMA
getOhlc
getShowChart
getStock
getStockInfo
getStockNames
resetSession
tse 上市
otc 上櫃
z 當盤成交價
tv 當盤成交量
v 累積成交量
b 揭示買價(從高到低，以_分隔資料)
g 揭示買量(配合b，以_分隔資料)
a 揭示賣價(從低到高，以_分隔資料)
f 揭示賣量(配合a，以_分隔資料)
o 開盤
h 最高
l 最低
y 昨收
u 漲停價
w 跌停價
tlong epoch毫秒數
d 最近交易日期(YYYYMMDD)
t 最近成交時刻(HH:MI:SS)
c 股票代號
n 公司簡稱
nf 公司全名
"""


def alignment(s, space):
  base = len(s)
  count = len(re.findall('[a-zA-Z0-9]', s))
  space = space - (2 * base) + count  # space - ((base - count) * 2) - count
  s = s + (' ' * space)
  return s


def colored(s, color):
  if color == 'green':
    return '\033[1;32m' + s + '\033[m'
  if color == 'red':
    return '\033[1;31m' + s + '\033[m'


class TWSELIB(object):

  def __init__(self):
    self.timestamp = int(time.time() * 1000) + 1000
    self.headers = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
      'Content-Type': 'text/html; charset=UTF-8',
      'Accept-Language': 'zh-TW'
    }
    self.headers['Cookie'] = self.get_cookie()
    pass

  def get_cookie(self):
    api_get_stock_cookie = 'http://mis.twse.com.tw/stock'
    r = requests.get(api_get_stock_cookie, headers=self.headers)
    return r.headers['Set-Cookie']

  def get_stock_key(self, stock_symbol):
    api_get_stock = "http://mis.twse.com.tw/stock/api/getStock.jsp"
    payload = {
      'json': 1,
      '_': self.timestamp,
      'ch': '{}.tw'.format(stock_symbol)
    }
    r = requests.get(api_get_stock, headers=self.headers, params=payload)
    return r.json()['msgArray'][0]['key']

  def get_stock_info(self, stock_keys):
    api_get_stock_info = "http://mis.twse.com.tw/stock/api/getStockInfo.jsp"
    payload = {
      'json': 1,
      '_': self.timestamp,
      'delay': 0,
      'ex_ch': '%7C'.join(stock_keys)
    }
    r = requests.get(api_get_stock_info, headers=self.headers, params=payload)
    try:
      if r.json()['msgArray']:
        return r.json()['msgArray']
    except KeyError as err:
      print("Key error: {}".format(err))
      return []


def print2terminal(stock_infos):
  if stock_infos:
    print('\n代號  商品          成交   漲跌    幅度    單量    總量   最高   最低   開盤')
    for stock in stock_infos:
      change = float(stock['z']) - float(stock['y'])
      change_p = change / float(stock['y'])
      stock_name = alignment(stock['n'], 11)
      stock_price = colored('{:>6}'.format(stock['z']), 'green') if change >= 0 else colored('{:>6}'.format(stock['z']), 'red')
      stock_change = colored('{:>+6.2f}'.format(change), 'green') if change >= 0 else colored('{:>+6.2f}'.format(change), 'red')
      stock_change_p = colored('{:>+7.2%}'.format(change_p), 'green') if change >= 0 else colored('{:>+7.2%}'.format(change_p), 'red')
      stock_change_high = colored('{:>6}'.format(stock['h']), 'green') if float(stock['h']) - float(stock['y']) >= 0 else colored('{:>6}'.format(stock['h']), 'red')
      stock_change_low = colored('{:>6}'.format(stock['l']), 'green') if float(stock['l']) - float(stock['y']) >= 0 else colored('{:>6}'.format(stock['l']), 'red')
      print("{:<5} {} {} {} {} {:>7,} {:>7,} {} {} {:>6}".format(stock['c'], stock_name, stock_price, stock_change, stock_change_p, int(stock['tv']), int(stock['v']), stock_change_high, stock_change_low, stock['o']))
    else:
      print('\n資料時間: {} {}'.format(stock['d'], stock['t']))


def main():
  stock_keys = []
  stock_symbols = []
  stock_interval = None
  stock_config = '~/.twsecli_config'

  # init config
  if not os.path.isfile(os.path.expanduser(stock_config)):
    with open(os.path.expanduser(stock_config), 'w', encoding='utf-8') as outf:
      outf.write('0050\n')
      outf.write('0056\n')

  # argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("symbol", nargs="*", help="stock symbol", type=int)
  parser.add_argument("-n", "--interval", metavar="", help="seconds to wait between updates, minimum 60s", type=int)
  parser.add_argument("-c", "--config", metavar="", help="stock symbol config, default path ~/.twsecli_config", type=int)
  argv = parser.parse_args()
  if argv.config:
    stock_config = argv.config
  if len(argv.symbol) == 0:
    try:
      print('讀取設定檔: {}'.format(os.path.expanduser(stock_config)))
      with open(os.path.expanduser(stock_config), 'r', encoding='utf-8') as inf:
        for line in inf:
          if line.strip():
            stock_symbols.append(line.strip())
    except OSError as err:
      print('OS error: {}'.format(err))
      return
  else:
    stock_symbols = argv.symbol
  if argv.interval:
    stock_interval = 60 if argv.interval < 60 else argv.interval

  # create object
  twse_lib = TWSELIB()
  for stock_symbol in stock_symbols:
    key = twse_lib.get_stock_key(stock_symbol)
    stock_keys.append(key)
  while True:
    stock_infos = twse_lib.get_stock_info(stock_keys)
    if stock_infos:
      if stock_interval:
        os.system('clear')
      print2terminal(stock_infos)
      if stock_interval:
        print('資料更新頻率: {}s'.format(stock_interval))
        time.sleep(argv.interval)
      else:
        break
    else:
      break

  # gc object
  del twse_lib
  pass


if __name__ == '__main__':
  main()
