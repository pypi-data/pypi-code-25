#!../futurav/bin/python
import traceback
import json
import urllib
import urllib2
import webbrowser
import re
import datetime
import time
import inspect
import os
import sys
import ssl
from copy import deepcopy
import pandas as pd
import numpy as np
from quant.stats import stats
from futuraAiUtils import loadTradingSystem, loadData, fillnans


def evalTradingStrat(tradingStrategy,
                     plotGraphs=True,
                     reloadData=False,
                     state={},
                     sourceData='tickerData'):
    ''' Main function that backtests a trading system.

    evaluates the trading strategy passed to it returns the evalued performance metrics.
    evalTradingStrat calls the trading system for each period on markets specified in the settinngs. 
    Evaluates the returns of each period to compose the backtest.

    Example:

    s = evalTradingStrat('tsName') evaluates the trading system specified in string tsName, and stores the result in dictionary s.

    Args:

        tsName (str): Specifies the trading system to be backtested
        plotGraphs (bool, optional): Show the equity curve plot after the evaluation
        reloadData (bool,optional): Force reload of market data.
        state (dict, optional):  State information to resume computation of an existing backtest (for live evaluation on Futura.ai servers). State needs to be of the same form as ret.

    Returns:
        a dict mapping keys to the relevant backesting information: trading strategy name, system equity, trading dates, market exposure, market equity, the errorlog, the run time, the system's statistics, and the evaluation date.

        keys and description:
            'tsName' (str):    Name of the trading system, same as tsName
            'fundDate' (int):  All dates of the backtest in the format YYYYMMDD
            'fundEquity' (float):    Equity curve for the fund (collection of all markets)
            'returns' (float): Marketwise returns of trading system
            'marketEquity' (float):    Equity curves for each market in the fund
            'marketExposure' (float):    Collection of the returns p of the trading system function. Equivalent to the percent expsoure of each market in the fund. Normalized between -1 and 1
            'settings' (dict):    The settings of the trading system as defined in file tsName
            'errorLog' (list): list of strings with error messages
            'runtime' (float):    Runtime of the evaluation in seconds
            'stats' (dict): Performance numbers of the backtest
            'evalDate' (datetime): Last market data present in the backtest

    Copyright Futura.ai LLC - March 2018
    '''

    errorlog = []
    ret = {}

    TSobject = loadTradingSystem(tradingStrategy)
    try:
        settings = TSobject.stratSettings()
        tsName = str(tradingStrategy)
    except Exception as e:
        print "Unable to load settings. Please ensure your settings definition is correct"
        print str(e)
        print traceback.format_exc()
        raise

    if isinstance(state, dict):
        if 'save' not in state:
            state['save'] = False
        if 'resume' not in state:
            state['resume'] = False
        if 'runtimeInterrupt' not in state:
            state['runtimeInterrupt'] = False
    else:
        print 'state variable is not a dict'

    # get boolean index of futures
    futuresIx = np.array(
        map(lambda string: bool(re.match("F_", string)), settings['markets']))

    # get data fields and extract them.
    requiredData = set(
        ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'P', 'RINFO', 'p'])
    dataToLoad = requiredData

    tsArgs = inspect.getargspec(TSobject.tradingStrategy)
    tsArgs = tsArgs[0]
    tsDataToLoad = [
        item for index, item in enumerate(tsArgs) if item.isupper()
    ]

    dataToLoad.update(tsDataToLoad)

    global settingsCache
    global dataCache

    if 'settingsCache' not in globals() or settingsCache != settings:
        if 'beginInSample' in settings and 'endInSample' in settings:
            dataMap = loadData(
                settings['markets'],
                dataToLoad,
                reloadData,
                beginInSample=settings['beginInSample'],
                endInSample=settings['endInSample'],
                dataDir=sourceData)
        elif 'beginInSample' in settings and 'endInSample' not in settings:
            dataMap = loadData(
                settings['markets'],
                dataToLoad,
                reloadData,
                settings['beginInSample'],
                dataDir=sourceData)
        elif 'endInSample' in settings and 'beginInSample' not in settings:
            dataMap = loadData(
                settings['markets'],
                dataToLoad,
                reloadData,
                endInSample=settings['endInSample'],
                dataDir=sourceData)
        else:
            dataMap = loadData(
                settings['markets'],
                dataToLoad,
                reloadData,
                dataDir=sourceData)

        dataCache = deepcopy(dataMap)
        settingsCache = deepcopy(settings)

    else:
        print 'copying data from cache'
        settings = deepcopy(settingsCache)
        dataMap = deepcopy(dataCache)

    print 'Evaluating Trading System'

    nMarkets = len(settings['markets'])
    endLoop = len(dataMap['DATE'])

    #print endLoop
    #exit()

    if 'RINFO' in dataMap:
        Rix = dataMap['RINFO'] != 0
    else:
        dataMap['RINFO'] = np.zeros(np.shape(dataMap['CLOSE']))
        Rix = np.zeros(np.shape(dataMap['CLOSE']))

    dataMap['exposure'] = np.zeros((endLoop, nMarkets))
    dataMap['equity'] = np.ones((endLoop, nMarkets))
    dataMap['fundEquity'] = np.ones((endLoop, 1))
    realizedP = np.zeros((endLoop, nMarkets))
    returns = np.zeros((endLoop, nMarkets))

    sessionReturnTemp = np.append(
        np.empty((1, nMarkets)) * np.nan,
        ((dataMap['CLOSE'][1:, :] - dataMap['OPEN'][1:, :]) /
         dataMap['CLOSE'][0:-1, :]),
        axis=0).copy()
    sessionReturn = np.nan_to_num(fillnans(sessionReturnTemp))
    #print sessionReturn
    #exit()
    gapsTemp = np.append(
        np.empty((1, nMarkets)) * np.nan,
        (dataMap['OPEN'][1:, :] - dataMap['CLOSE'][:-1, :] -
         dataMap['RINFO'][1:, :].astype(float)) / dataMap['CLOSE'][:-1:],
        axis=0)
    gaps = np.nan_to_num(fillnans(gapsTemp))

    # check if a default slippage is specified
    if False == settings.has_key('slippage'):
        settings['slippage'] = 0.05

    slippageTemp = np.append(
        np.empty((1, nMarkets)) * np.nan,
        ((dataMap['HIGH'][1:, :] - dataMap['LOW'][1:, :]
          ) / dataMap['CLOSE'][:-1, :]),
        axis=0) * settings['slippage']
    SLIPPAGE = np.nan_to_num(fillnans(slippageTemp))
    #print 'SLIPPAGE=',SLIPPAGE
    if 'lookback' not in settings:
        startLoop = 2
        settings['lookback'] = 1
    else:
        startLoop = settings['lookback'] - 1

    # Server evaluation --- resumes for new day.
    if state['resume']:
        if 'evalData' in state:
            ixOld = dataMap['DATE'] <= state['evalData']['evalDate']
            evalData = state['evalData']

            ixMapExposure = np.concatenate(([False, False], ixOld), axis=0)
            dataMap['equity'][ixOld, :] = state['evalData']['marketEquity']
            dataMap['exposure'][ixMapExposure, :] = state['evalData'][
                'marketExposure']
            dataMap['fundEquity'][ixOld, :] = state['evalData']['fundEquity']

            startLoop = np.shape(state['evalData']['fundDate'])[0]
            endLoop = np.shape(dataMap['DATE'])[0]

            print('Resuming' + tsName + ' | computing ' +
                  str(endLoop - startLoop + 1) + ' new days')
            settings = evalData['settings']

    t0 = time.time()

    # Loop through trading days
    for t in range(startLoop, endLoop):
        profitForToday = dataMap['exposure'][t - 1, :]

        yesterdaysP = realizedP[t - 2, :]
        deltaP = profitForToday - yesterdaysP

        newGap = yesterdaysP * gaps[t, :]
        newGap[np.isnan(newGap)] = 0

        newRet = profitForToday * sessionReturn[t, :] - abs(
            deltaP * SLIPPAGE[t, :])
        newRet[np.isnan(newRet)] = 0

        returns[t, :] = newRet + newGap

        dataMap['equity'][t, :] = dataMap['equity'][t - 1, :] * (
            1 + returns[t, :])
        dataMap['fundEquity'][t] = (dataMap['fundEquity'][t - 1] *
                                    (1 + np.sum(returns[t, :])))

        realizedP[t - 1, :] = dataMap['CLOSE'][t, :] / dataMap['CLOSE'][
            t - 1, :] * dataMap['fundEquity'][t - 1] / dataMap['fundEquity'][
                t] * profitForToday

        # Roll futures contracts.
        if np.any(Rix[t, :]):
            delta = np.tile(dataMap['RINFO'][t, Rix[t, :]], (t, 1))
            dataMap['CLOSE'][0:t, Rix[
                t, :]] = dataMap['CLOSE'][0:t,
                                          Rix[t, :]].copy() + delta.copy()
            dataMap['OPEN'][0:t, Rix[
                t, :]] = dataMap['OPEN'][0:t, Rix[t, :]].copy() + delta.copy()
            dataMap['HIGH'][0:t, Rix[
                t, :]] = dataMap['HIGH'][0:t, Rix[t, :]].copy() + delta.copy()
            dataMap['LOW'][0:t, Rix[
                t, :]] = dataMap['LOW'][0:t, Rix[t, :]].copy() + delta.copy()

        try:
            argList = []

            for index in range(len(tsArgs)):
                if tsArgs[index] == 'settings':
                    argList.append(settings)
                elif tsArgs[index] == 'self':
                    continue
                else:
                    argList.append(dataMap[tsArgs[index]][
                        t - settings['lookback'] + 1:t + 1].copy())
            #print argList
            #exit()
            position, settings = TSobject.tradingStrategy(*argList)
        except:
            print 'Error evaluating trading system'
            print sys.exc_info()[0]
            print traceback.format_exc()
            errorlog.append(
                str(dataMap['DATE'][t]) + ': ' + str(sys.exc_info()[0]))
            dataMap['equity'][t:, :] = np.tile(dataMap['equity'][t, :],
                                               (endLoop - t, 1))
            return
        position[np.isnan(position)] = 0
        position = np.real(position)
        position = position / np.sum(abs(position))
        position[np.isnan(
            position)] = 0  # extra nan check in case the positions sum to zero

        dataMap['exposure'][t, :] = position.copy()

        t1 = time.time()
        runtime = t1 - t0
        if runtime > 300 and state['runtimeInterrupt']:
            errorlog.append('Evaluation stopped: Runtime exceeds 5 minutes.')
            break

    if 'budget' in settings:
        fundequity = dataMap['fundEquity'][(
            settings['lookback'] - 1):, :] * settings['budget']
    else:
        fundequity = dataMap['fundEquity'][(settings['lookback'] - 1):, :]
    #print '---fundequity---:',fundequity
    #print '---dataMap[exposure]---:',dataMap

    marketRets = np.float64(
        dataMap['CLOSE'][1:, :] - dataMap['CLOSE'][:-1, :] -
        dataMap['RINFO'][1:, :]) / dataMap['CLOSE'][:-1, :]
    marketRets = fillnans(marketRets)
    marketRets[np.isnan(marketRets)] = 0
    marketRets = marketRets.tolist()
    a = np.zeros((1, nMarkets))
    a = a.tolist()
    marketRets = a + marketRets

    ret['returns'] = np.nan_to_num(returns).tolist()

    if errorlog:
        print 'Error: {}'.format(errorlog)

    if plotGraphs:
        statistics = stats(fundequity)
        print statistics
        if (settings.get('backend', 'tk') == 'tk'):
            from guiBackends.tkbackend import renderVisualizations
        else:
            from guiBackends.bokehbackend import renderVisualizations
        returns = renderVisualizations(
            tradingStrategy, fundequity, dataMap['equity'],
            dataMap['exposure'], settings,
            dataMap['DATE'][settings['lookback'] - 1:], statistics,
            ret['returns'], marketRets)

    else:
        statistics = stats(fundequity)

    ret['tsName'] = tsName
    ret['fundDate'] = dataMap['DATE'].tolist()
    ret['fundEquity'] = dataMap['fundEquity'].tolist()
    ret['marketEquity'] = dataMap['equity'].tolist()
    ret['marketExposure'] = dataMap['exposure'].tolist()
    ret['errorLog'] = errorlog
    ret['runtime'] = runtime
    ret['stats'] = statistics
    ret['settings'] = settings
    ret['evalDate'] = dataMap['DATE'][t]
    #print ret
    if state['save']:
        with open(tsName + '.json', 'w+') as fileID:
            stateSave = json.dump(ret, fileID)
    return ret


#    return True
def computeFees(equityCurve, managementFee, performanceFee):
    ''' computes equity curve after fees

    Args:
        equityCurve (list, numpy array) : a column vector of daily fund values
        managementFee (float) : the management fee charged to the investor (a portion of the AUM charged yearly)
        performanceFee (float) : the performance fee charged to the investor (the portion of the difference between a new high and the most recent high, charged daily)

    Returns:
        returns an equity curve with the fees subtracted.  (does not include the effect of fees on equity lot size)

    '''
    returns = (np.array(equityCurve[1:]) - np.array(equityCurve[:-1])
               ) / np.array(equityCurve[:-1])
    ret = np.append(0, returns)

    tradeDays = ret > 0
    firstTradeDayRow = np.where(tradeDays is True)
    firstTradeDay = firstTradeDayRow[0][0]

    manFeeIx = np.zeros(np.shape(ret), dtype=bool)
    manFeeIx[firstTradeDay:] = 1
    ret[manFeeIx] = ret[manFeeIx] - managementFee / 252

    ret = 1 + ret
    r = np.ndarray((0, 0))
    high = 1
    last = 1
    pFee = np.zeros(np.shape(ret))
    mFee = np.zeros(np.shape(ret))

    for k in range(len(ret)):
        mFee[k] = last * managementFee / 252 * equityCurve[0][0]
        if last * ret[k] > high:
            iFix = high / last
            iPerf = ret[k] / iFix
            pFee[k] = (iPerf - 1) * performanceFee * iFix * equityCurve[0][0]
            iPerf = 1 + (iPerf - 1) * (1 - performanceFee)
            r = np.append(r, iPerf * iFix)
        else:
            r = np.append(r, ret[k])
        if np.size(r) > 0:
            last = r[-1] * last
        if last > high:
            high = last

    out = np.cumprod(r)
    out = out * equityCurve[0]

    return out
