#!/usr/bin/python
# Authors: Mabel Villalba Jimenez <mabelvj@gmail.com>,
#          Emilio Molina Martinez <emilio.mol.mar@gmail.com>
# License: GPLv3

"""
    Example of usage.
    To run do in the command line: bokeh serve main.py
"""
import numpy as np
import pandas as pd
from stocksdashboard import *
from stocksdashboard import StocksDashboard
import sys
print(sys.path)
import pdb
pdb.set_trace()
from dashboard_with_widgets import DashboardWithWidgets
from bokeh.sampledata.stocks import AAPL
from bokeh.layouts import row, widgetbox
from bokeh.io import curdoc
from bokeh.server.server import Server


column = 'adj_close'

data = pd.DataFrame(AAPL[column], index=pd.date_range(
    start='1/1/2018', periods=len(AAPL[column])), columns=[column])
data_ema = data.ewm(span=int(
    np.round((252. / 12.) * 1.)),
    min_periods=1,
    adjust=True,
    ignore_na=False).mean()[column]

# Multiple formats for each line.
sdb = StocksDashboard()
sdb.build_dashboard(
    input_data={'stocks': {'STOCK': data},
                'ema': {'STOCK_ema': data_ema}},
    aligment={'stocks': {'STOCK': 'left'},
              'ema': {'STOCK_ema': None}},
    line_width=2.5, column=column, show=False)
layout = sdb.layout

dict_signals = {'STOCK_ema': "STOCK.ewm(span=w," +
                             "min_periods=1, " +
                             "adjust=True,ignore_na=False)" +
                             ".mean()"}
dbw = DashboardWithWidgets(
    sdb,
    sliders_params={'w': {'title': 'EMA window',
                          'params': {
                              'value': 20,
                              'start': 2,
                              'end': 252,
                              'step': 5}
                          }},
    signals_expressions=dict_signals)
sliders = dbw.create_sliders()
dbw.widget_on_change()

plot_width = 980
tab_title = 'plot'

inputs = widgetbox(list(sliders.values()))

curdoc().add_root(row(inputs, layout, width=plot_width))
curdoc().title = tab_title
