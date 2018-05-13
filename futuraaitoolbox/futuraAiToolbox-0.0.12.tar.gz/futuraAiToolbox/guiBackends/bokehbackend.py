#!/home/tanmay/dev/futuraAi/genesisrepo/futurav/bin/python
# -*- coding: utf-8 -*-
""" Gui backend using python bokeh plot
Requires any modern browser. Recommended browsers are Chrome/Opera/Firefox
This module documentations style is  taken from `Google Python Style Guide`_.

Main function that this module provide is 
    literal blocks::

        $ renderVisualizations

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import numpy as np
from datetime import datetime as dt
from tornado.ioloop import IOLoop
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models.widgets import PreText, Select, Dropdown, DataTable, DateFormatter, TableColumn
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.server.server import Server
from bokeh.plotting import figure, output_file
from bokeh.layouts import gridplot, layout, row, column, WidgetBox
from bokeh.palettes import brewer
from bokeh.themes import Theme
import numpy as np
from futuraAiToolbox.quant.stats import stats as qstats
import os

# globals
IOLOOP = IOLoop.current()
strptime = dt.strptime
hover = HoverTool(tooltips=[
    ("index", "$index"),
    ("(x,y)", "($x, $y)"),
    ("desc", "@desc"),
])
dirname = os.path.dirname
path = dirname(__file__)
# theme = Theme(filename="{}/theme.yaml".format(path))
TOOLS = "pan,wheel_zoom,box_zoom,reset, hover"
TP_TITLE = "Trading performance {}"
EXP_TITLE = "Exposure : {}"
MR_TITLE = "Market Returns: {}"
LONG_SHORT_LABLES=['Long&Short', 'Long', 'Short']

# end globals

def renderVisualizations(tradingSystem, equity, mEquity, exposure, settings,
                         dateList, statistics, returns, marketReturns):
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
    datetime = lambda x: np.array(x, dtype=np.datetime64)
    output_file("backendResult.html", title="Results visualizer")
    # generated globals and preparations for charts
    all_markets = list(settings['markets'])
    equity_lables = ['Trading Strategy'] + ["{}".format(x) for x in all_markets]

    statsLables = {'sortino': 'Sortino Ratio', 'maxDD': 'Maximum Drawdown',
                    'sharpe': 'Sharpe Ratio', 'returnYearly':'Performance', 'volaYearly': 'Volatility',
                    'maxTimeOffPeak':'Max Time off peak'}
    statsDict = dict(
        statName = [statsLables[k] for k in statsLables.keys()],
        statValue = [statistics[k] for k in statsLables.keys()]
        )
    statsSource = ColumnDataSource(statsDict)

    dateRange = [strptime(str(d), '%Y%m%d') for d in dateList]

    # cash offset
    cashOffset = 0
    try:
        mRetMarkets.remove('CASH')
        cashOffset = 1
    except:
        pass
    # end cash offset
    # mEquity has data by timeslice for each equity so let’s make it data by equity all times
    tradingPerfEquities  = np.transpose(np.array(mEquity))
    marketRet = np.transpose(np.array(marketReturns))
    returnForTradingStrat = equity[:,0]
    # import pdb
    # pdb.set_trace()
    data = {
        'timeline':dateRange,
        'yReturns': returnForTradingStrat
        }

    dataReturns = {
        'timeline':dateRange,
        'yReturns': np.cumprod(1 + marketRet[cashOffset])
        }

    sourceReturns = ColumnDataSource(data=dataReturns)
    source = ColumnDataSource(data=data)
    dataDD = {
                'tMaxDD':[],
                'yMaxDD':[]}
    dataOffPeak = {
                'tMaxTimeOffPeak':[],
                'yMaxTimeOffPeak':[]
        }
    sourceDD = ColumnDataSource(data = dataDD)
    sourceOffPeak = ColumnDataSource(data = dataOffPeak)
    Long = np.transpose(np.array(exposure))
    Long[Long < 0] = 0
    Long = Long[:, (
        settings['lookback'] - 2):-1]  # Market Exposure lagged by one day

    Short = -np.transpose(np.array(exposure))
    Short[Short < 0] = 0
    Short = Short[:, (settings['lookback'] - 2):-1]
    returnsList = np.transpose(np.array(returns))
    returnLong = np.transpose(np.array(exposure))
    returnLong[returnLong < 0] = 0
    returnLong[returnLong > 0] = 1
    returnLong = np.multiply(
        returnLong[:, (settings['lookback'] - 2):-1], returnsList[:, (
            settings['lookback'] - 1):])  # y values for Long Only Equity Curve

    returnShort = -np.transpose(np.array(exposure))
    returnShort[returnShort < 0] = 0
    returnShort[returnShort > 0] = 1
    returnShort = np.multiply(
        returnShort[:, (settings['lookback'] - 2):-1],
        returnsList[:, (settings['lookback'] - 1
                        ):])  # y values for Short Only Equity Curve
    # end generated globals
    print all_markets
    
    def modify_doc(doc):
        # ddtp = None
        # dropdownTP = Select(
        #     value=ddtp, title="Trading Performance", options=menuTradingPerf)
        # stats on top
        def statsTable():
            # todo: remove the ’#’
            columns = [TableColumn(field="statName", title="Statistics"),
                    TableColumn(field="statValue", title="Value"),]
            data_table = DataTable(source=statsSource, columns=columns, height=200)
                                   # , width=400, height=280)
            return data_table

        # main plot function
        def plotLongShort():
            p1 = figure(x_axis_type="datetime", y_axis_type="linear",
                        title="Market Returns",tools=TOOLS)
            p1.grid.grid_line_alpha = 0
            p1.xaxis.axis_label = 'Date'
            p1.yaxis.axis_label = 'Long/Short'
            # p1.ygrid.band_fill_color = "green"
            p1.ygrid.band_fill_alpha = 0.2
            p1.line(x=dateRange, y=Long.sum(axis=0), color="green", line_width=1.5)
            p1.line(x=dateRange, y=Short.sum(axis=0), color="red", line_width=1.5)
            return p1

        
        def plotMR():
            p1 = figure(x_axis_type="datetime", y_axis_type="linear",
                        title="Market Returns",tools=TOOLS)
            p1.grid.grid_line_alpha = 0
            p1.xaxis.axis_label = 'Date'
            p1.yaxis.axis_label = 'Returns'
            # p1.ygrid.band_fill_color = "green"
            p1.ygrid.band_fill_alpha = 0.2
            p1.line(x='timeline', y='yReturns', source=sourceReturns,
                    legend='Returns',color='grey', line_width=1.5)
        
            return p1

        def plotTP(instr="Trading Strategy"):
            # figure specific setup
            p1 = figure(x_axis_type="datetime", y_axis_type="linear",
                        title=TP_TITLE.format(instr),tools=TOOLS)
            p1.grid.grid_line_alpha = 0
            p1.xaxis.axis_label = 'Date'
            p1.yaxis.axis_label = 'Price'
            # p1.ygrid.band_fill_color = "olive"
            p1.ygrid.band_fill_alpha = 0.2
            # end setup
            # figure data
            lon = Long.sum(axis=0)
            sho = Short.sum(axis=0)
            # end data

            p1.line(x='timeline', y='yReturns', source=source,
                    legend='Returns',color='blue', line_width=1.5)

            if np.isnan(statistics['maxDDBegin']) == False:
                dataDD['tMaxDD'] = dateRange[statistics['maxDDBegin']: statistics['maxDDEnd'] + 1]
                dataDD['yMaxDD'] = source.data['yReturns'][statistics['maxDDBegin']: statistics['maxDDEnd'] + 1]
                if not (np.isnan(statistics['maxTimeOffPeakBegin'])) and not (
                    np.isnan(statistics['maxTimeOffPeak'])):
                    dataOffPeak['tMaxTimeOffPeak'] = dateRange[(statistics['maxTimeOffPeakBegin'] + 1):(
                        statistics['maxTimeOffPeakBegin'] +
                        statistics['maxTimeOffPeak'] + 2)]
                    dataOffPeak['yMaxTimeOffPeak'] =  source.data['yReturns'][statistics['maxTimeOffPeakBegin'] + 1] * np.ones(
                                    (statistics['maxTimeOffPeak'] + 1))
                    # dataDD['tMaxTimeOffPeak'] = dateRange[statistics['maxTimeOffPeakBegin'] : statistics['maxTimeOffPeakEnd'] + 1]
                    # dataDD['yMaxTimeOffPeak'] = source.data['yReturns'][statistics['maxTimeOffPeakBegin']: statistics['maxTimeOffPeakEnd'] + 1]
                sourceDD.data = dataDD
                sourceOffPeak.data = dataOffPeak
            p1.line(
                x='tMaxDD',
                y='yMaxDD',
                source=sourceDD,
                line_width = 2.5,
                legend='Max DrawDown',
                color='red')
            p1.line(
                x='tMaxTimeOffPeak',
                y='yMaxTimeOffPeak',
                line_width = 2.5,
                line_dash='dotted',
                source=sourceOffPeak,
                legend='Max Time Off peak',
                color='red')
            return p1

        # callbacks

        def equityChanged(attr, old, new):
            print "New equity selected !!! {}".format(new)
            # indx_TradingPerf = indexl(fundEquityLbl, new)
            # indx_MarketRet = indexl(marketReturnLbl, dropdownMR.value)
            # indx_Exposure = indexl(exposureLbl, dropdownTP.value)
            plot_tp.title.text = TP_TITLE.format(new)
            update(equity = new, position=dropdownLongShort.value)

        def longShortChanged(attr, old, new):
            update(equity = dropdownEquity.value, position=new)

        def newMarketSelected(attr, old, new):
            equity = "Trading Strategy" if dropdownEquity.value == '' else dropdownEquity.value
            position = "Long&Short" if dropdownLongShort.value =='' else dropdownLongShort.value
            indx_MarketRet = all_markets.index(new)
            if position == "Short":
                dataReturns['yReturns'] = np.cumprod(1 - marketRet[indx_MarketRet + cashOffset])
            else:
                dataReturns['yReturns'] = np.cumprod(1 + marketRet[indx_MarketRet + cashOffset])
            sourceReturns.data = dataReturns
            statistics = qstats(dataReturns['yReturns'])
            print "statistics ==========================================================="
            print statistics
            print "statistics ==========================================================="
            # let’s update stats too
            statsDict['statValue'] = [statistics[k] for k in statsLables.keys()]
            statsSource.data = statsDict


        # end callback 
        # universal update
        def update(equity=None, position=None):
            equity = "Trading Strategy" if equity == '' else equity
            position = "Long&Short" if position =='' else position
            print "equity => {}, position => {}".format(equity, position)
            if equity == "Trading Strategy":
                lon = Long.sum(axis=0)
                sho = Short.sum(axis=0)
                # y_Long = lon
                # y_Short = sho
                if position == "Long&Short":  # Long & Short selected
                    data['yReturns']= returnForTradingStrat # equity
                elif position == "Long":  # Long Selected
                    data['yReturns'] = settings['budget'] * np.cumprod(
                        1 + returnLong.sum(axis=0))
                else:  # Short Selected
                    data['yReturns'] = settings['budget'] * np.cumprod(
                        1 + returnShort.sum(axis=0))
                    # data['yReturns'] = returnForTradingStrat
                    # plot_tp.figure.y_axis_type = 'log'
            else: #individual market selected
                indx_equity = equity_lables.index(equity)
                y_Long = Long[indx_equity - 1]
                y_Short = Short[indx_equity - 1]
                if position == "Long&Short":
                    data['yReturns'] = tradingPerfEquities[indx_equity-1]
                elif position == "Long":
                    data['yReturns'] = np.cumprod(1 + returnLong[indx_equity - 1])
                elif position == "Short":
                    data['yReturns'] = np.cumprod(1 + returnShort[indx_equity - 1])
                # plot_tp.figure.y_axis_type = 'linear'

            source.data = data

            statistics = qstats(data['yReturns'])
            print "statistics ==========================================================="
            print statistics
            print "statistics ==========================================================="
            statsDict['statValue'] = [statistics[k] for k in statsLables.keys()]
            statsSource.data = statsDict
            # update drawdowns etc as well
            if np.isnan(statistics['maxDDBegin']) == False:
                dataDD['tMaxDD'] = dateRange[statistics['maxDDBegin']: statistics['maxDDEnd'] + 1]
                dataDD['yMaxDD'] = source.data['yReturns'][statistics['maxDDBegin']: statistics['maxDDEnd'] + 1]
                if not (np.isnan(statistics['maxTimeOffPeakBegin'])) and not (
                    np.isnan(statistics['maxTimeOffPeak'])):
                    dataOffPeak['tMaxTimeOffPeak'] = dateRange[(statistics['maxTimeOffPeakBegin'] + 1):(
                        statistics['maxTimeOffPeakBegin'] +
                        statistics['maxTimeOffPeak'] + 2)]
                    dataOffPeak['yMaxTimeOffPeak'] =  source.data['yReturns'][statistics['maxTimeOffPeakBegin'] + 1] * np.ones(
                                    (statistics['maxTimeOffPeak'] + 1))
                sourceDD.data = dataDD
                sourceOffPeak.data = dataOffPeak

        # create charting object
        plot_tp = plotTP()
        plot_mr = plotMR()
        plot_longShort = plotLongShort()
        statsBox = statsTable()
        menuEquity = [(x, x) for x in equity_lables]
        # dropdownExp = Dropdown(label="Exposure", button_type="warning",
        #                        menu=menuExposure)
        dropdownEquity = Select(title="Trading Performances", options=equity_lables)
        dropdownLongShort = Select(title="Long/Short", options=LONG_SHORT_LABLES)
        dropdownMarketReturns = Select(title="Market Returns", options=all_markets)
        #setup callbacks for selets
        dropdownEquity.on_change('value', equityChanged)
        dropdownLongShort.on_change('value', longShortChanged)
        dropdownMarketReturns.on_change('value', newMarketSelected)
        dw1 = WidgetBox(dropdownEquity)
        dw2 = WidgetBox(dropdownLongShort)
        dw3 = WidgetBox(dropdownMarketReturns)
        widgets = row(dw1, dw2, dw3, sizing_mode='scale_width')
        main_plots = row(plot_tp,plot_longShort, plot_mr, sizing_mode='scale_width')
        stats = row(statsBox, sizing_mode='scale_width')
        custlayout = layout(
            stats,
            widgets,
            main_plots,
            sizing_mode='scale_width')
        # doc.theme=theme
        doc.add_root(custlayout)

    # start bokeh io loop
    bokeh_app = Application(FunctionHandler(modify_doc))
    server = Server({'/': bokeh_app}, io_loop=IOLOOP)
    server.start()
    print('Opening Bokeh application on http://localhost:5006/')
    print('Press Ctrl-C to exit ..')
    IOLOOP.add_callback(server.show, "/")
    IOLOOP.start()

    # end start


def indexl(l, v):
    try:
        return l.index(v)
    except:
        return -1
