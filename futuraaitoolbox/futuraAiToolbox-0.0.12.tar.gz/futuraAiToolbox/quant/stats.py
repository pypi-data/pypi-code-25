import numpy as np


def stats(equityCurve):
    ''' calculates trading system statistics

    Calculates and returns a dict containing the following statistics
    - sharpe ratio
    - sortino ratio
    - annualized returns
    - annualized volatility
    - maximum drawdown
        - the dates at which the drawdown begins and ends
    - the MAR ratio
    - the maximum time below the peak value
        - the dates at which the max time off peak begin and end

    Args:
        equityCurve (list): the equity curve of the evaluated trading system

    Returns:
        statistics (dict): a dict mapping keys to corresponding trading system statistics (sharpe ratio, sortino ration, max drawdown...)

    Copyright Futura.ai LLC - March 2018

    '''
    returns = (equityCurve[1:] - equityCurve[:-1]) / equityCurve[:-1]

    volaDaily = np.std(returns)
    volaYearly = np.sqrt(252) * volaDaily

    index = np.cumprod(1 + returns)
    indexEnd = index[-1]

    returnDaily = np.exp(np.log(indexEnd) / returns.shape[0]) - 1
    returnYearly = (1 + returnDaily)**252 - 1
    sharpeRatio = returnYearly / volaYearly

    downsideReturns = returns.copy()
    downsideReturns[downsideReturns > 0] = 0
    downsideVola = np.std(downsideReturns)
    downsideVolaYearly = downsideVola * np.sqrt(252)

    sortino = returnYearly / downsideVolaYearly

    highCurve = equityCurve.copy()

    testarray = np.ones((1, len(highCurve)))
    test = np.array_equal(highCurve, testarray[0])

    if test:
        mX = np.NaN
        mIx = np.NaN
        maxDD = np.NaN
        mar = np.NaN
        maxTimeOffPeak = np.NaN
        mtopStart = np.NaN
        mtopEnd = np.NaN
    else:
        for k in range(len(highCurve) - 1):
            if highCurve[k + 1] < highCurve[k]:
                highCurve[k + 1] = highCurve[k]

        underwater = equityCurve / highCurve
        mi = np.min(underwater)
        mIx = np.argmin(underwater)
        maxDD = 1 - mi
        mX = np.where(highCurve[0:mIx - 1] == np.max(highCurve[0:mIx - 1]))
        #        highList = highCurve.copy()
        #        highList.tolist()
        #        mX= highList[0:mIx].index(np.max(highList[0:mIx]))
        mX = mX[0][0]
        mar = returnYearly / maxDD

        mToP = equityCurve < highCurve
        mToP = np.insert(mToP, [0, len(mToP)], False)
        mToPdiff = np.diff(mToP.astype('int'))
        ixStart = np.where(mToPdiff == 1)[0]
        ixEnd = np.where(mToPdiff == -1)[0]

        offPeak = ixEnd - ixStart
        if len(offPeak) > 0:
            maxTimeOffPeak = np.max(offPeak)
            topIx = np.argmax(offPeak)
        else:
            maxTimeOffPeak = 0
            topIx = np.zeros(0)

        if np.not_equal(np.size(topIx), 0):
            mtopStart = ixStart[topIx] - 2
            mtopEnd = ixEnd[topIx] - 1

        else:
            mtopStart = np.NaN
            mtopEnd = np.NaN
            maxTimeOffPeak = np.NaN

    statistics = {}
    statistics['sharpe'] = sharpeRatio
    statistics['sortino'] = sortino
    statistics['returnYearly'] = returnYearly
    statistics['volaYearly'] = volaYearly
    statistics['maxDD'] = maxDD
    statistics['maxDDBegin'] = mX
    statistics['maxDDEnd'] = mIx
    statistics['mar'] = mar
    statistics['maxTimeOffPeak'] = maxTimeOffPeak
    statistics['maxTimeOffPeakBegin'] = mtopStart
    statistics['maxTimeOffPeakEnd'] = mtopEnd

    return statistics
