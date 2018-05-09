from .context import zen
import zen.data_proxy as data
import talib
import numpy as np
import pandas as pd


class Instrument:
    def __init__(self, secid, asset):
        self.secid = secid
        self.asset = asset

    def ma_rating(self, date=None):
        periods = [233, 144, 89, 55, 34, 21, 13, 5]
        history = data.get_local_data(
            self.secid, asset=self.asset, end=date).iloc[-periods[0]:]
        mas = [talib.SMA(history.close.values, p)[-1] for p in periods]
        close = history.loc[history.index[-1], 'close']
        mask = [close > ma for ma in mas]
        mas.append(close)
        mas.sort()
        try:
            position = 8 - mask.index(True)
        except ValueError:
            position = 0

        return position, mas.index(close)


class Index(Instrument):
    def __init__(self, secid):
        Instrument.__init__(self, secid, asset='INDEX')


class Stock(Instrument):
    def __init__(self, secid):
        Instrument.__init__(self, secid, asset='E')

    def boards(self):
        '''
        return a DataFrame like below:
              c_code      c_name
        700   885311.TI   智能电网
        5142  885461.TI    充电桩
        6913  885531.TI   光伏概念
        1107  881120.TI   电气设备
        '''
        return data.belong_to_boards(self.secid)


class Board:
    def __init__(self, c_code=None, c_name=None):
        self.c_code = c_code or data.cname_to_ccode(c_name)
        self.c_name = c_name or data.ccode_to_cname(c_code)

    def stocks(self):
        return data.get_index_stocks(c_code=self.c_code)

    def stock_ma_ratings(self, date=None):
        d = {}
        for s in self.stocks():
            try:
                rating = Stock(s).ma_rating(date)
            except KeyError:
                pass
            else:
                d[s] = rating
        return pd.DataFrame(d).T.sort_values(by=[0, 1], ascending=False)

    def ma_rating(self, date=None):
        return self.stock_ma_ratings(date).mean().values


class AllInstruments:
    def boards(self):
        return data.all_boards()

    def stocks(self):
        return data.all_stocks()

    def board_ma_ratings(self, date=None):
        d = {}
        for b in self.boards():
            try:
                rating = Board(b).ma_rating()
            except KeyError:
                pass
            else:
                d[b] = rating

        return pd.DataFrame(d).T.sort_values(by=[0, 1], ascending=False)
