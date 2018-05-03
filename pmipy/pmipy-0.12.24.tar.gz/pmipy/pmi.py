"""
Created on Sat Apr 21 07:29:46 2018

@author: jasonai
"""

from pmipy import log
import datetime


logger = log.createCustomLogger('root')

def execInfo(arg = True):
    if arg:
        def _deco(func):
            def wrapper(*arg, **kwargs):
                startTime = datetime.datetime.now()
                logger.info("start %s..."%func.__name__)
                func(*arg, **kwargs)
                endTime = datetime.datetime.now()
                secs = endTime - startTime
                logger.info("end {0}--> elapsed time: {1}".format(func.__name__, secs))
            return wrapper
    else:
        def _deco(func):
            return func
    return _deco


def checkResult(keyword, loopTime):
    def _deco(func):
        def wrapper(*arg, **kwargs):
            res2 = keyword
            time = 1
            while res2 == keyword and time <= loopTime:
                res = func(*arg, **kwargs)
                # 目前只考虑函数返回结果为list、字符串和数字这三种类型
                res2 = res[0] if type(res)==list else res 
                time += 1
            return res
        return wrapper

    return _deco

