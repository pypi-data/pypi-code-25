import log

def execInfo(arg = True):
    logger = log.createCustomLogger('root')
    if arg:
        def _deco(func):
            def wrapper(*arg, **kwargs):
                logger.info("# start %s..."%func.__name__)
                func(*arg, **kwargs)
                logger.info("# %s is end!" % func.__name__)
            return wrapper
    else:
        def _deco(func):
            return func
    return _deco

