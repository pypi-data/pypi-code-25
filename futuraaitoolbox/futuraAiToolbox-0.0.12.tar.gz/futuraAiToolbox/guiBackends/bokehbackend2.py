#!home/tanmay/dev/futuraAi/futurAiv/bin/python
# -*- coding: utf-8 -*-
""" Gui backend using bokeh plot.
Requires some modern browser.
Chrome/Chromium/Opera/Firexfox recommended

As this requires some extra setup while using from virtual environment

This module documentations is taken from `Google Python Style Guide`_.

Todo:
"""
from datetime import datetime as dt
from tornado.ioloop import IOLoop
from bokeh.models import HoverTool
import numpy as np

# global setup for bokeh and the mini server goes here

IO_LOOP = IOLoop.current()

STRPTIME = dt.strptime

HOVER = HoverTool(tooltips=[
    ("index", "$index"),
    ("(date,value)", "($x, $y)"),
    ("desc", "@desc"),
])
TOOLS = "pan,wheel_zoom,box_zoom,reset, hover"

#Charts title global
TP_TITLE = "Trading performance {}"
EXP_TITLE = "Exposure : {}"
MR_TITLE = "Market Returns: {}"
STATS_FMTSTR = """Sharpe Ratio = {sharpe:.4f}\t\tSortino Ratio = {sortino:.4f}\t\tPerformance (%/yr) = {returnYearly:.4f}\n\nVolatility (%/yr)  = {volaYearly:.4f}\t\tMax Drawdown = {maxDD:.4f}\t\tMAR Ratio = {mar:.4f}\n\nMax Time off peak =  {maxTimeOffPeak}\n\n\n\n\n\n"""


def renderVisualizations(tradingSystem,
                         equity,
                         mEquity,
                         exposure,
                         settings,
                         dateList,
                         statistics,
                         returns,
                         marketReturns):
    ''' plots equity curve and calculates trading system statistics

    Args:
    tradingSystem: Just in case we need some settings in future
    equity (list): list of equity of evaluated trading system.
    mEquity (list): list of equity of each market over the trading days.
    exposure (list): list of positions over the trading days.
    settings (dict): list of settings.
    dateList (list): list of dates corresponding to entries in equity.

    Copyright Futura.ai LLC - March 2018
    '''
    # globals and settings
    datetime = lambda x: np.array(x, dtype=np.datetime64)
    # end settings
    all_markets = list(settings['markets'])
    market_return_labels = map(lambda mkt: "{}".format(mkt),
                                   all_markets)
    fund_equity_lables = ['fundEquity'] + market_return_labels
    long_short_label = ['Long&Short', 'Long', 'Short']
