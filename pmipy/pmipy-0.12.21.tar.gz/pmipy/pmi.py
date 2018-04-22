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

