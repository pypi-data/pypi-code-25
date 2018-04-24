#!/usr/bin/env python
# encoding: utf-8


"""
Basic helper tools for text processing.
"""
import os
import time
from functools import wraps, partial


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print 'func:%r args:[%r, %r] took: %2.4f sec' % \
              (f.__name__, args, kw, te - ts)
        return result

    return wrap


def retry(exception, tries=4, delay=3, back_off=2, logger=None):
    """Retry calling the decorated function using an exponential back-off.

    Source:

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param exception: the exception to check. may be a tuple of
        exceptions to check
    :type exception: Exception or tuple

    :param tries: number of times to try (not retry) before giving up
    :type tries: int

    :param delay: initial delay between retries in seconds
    :type delay: int

    :param back_off: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type back_off: int

    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance

    """

    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exception, e:
                    msg = "%s, Retrying in %d seconds..." % (str(e).upper(), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print msg
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= back_off
            return f(*args, **kwargs)

        return f_retry

    return deco_retry


def decorator_normal_filter(func, check=None, logger=None):
    """
    A function decorator for filtering

    :param logger: Logger object

    :param func: Function to be decorated, which returns an iterable list.

    :param check: Filter function

    :return: Filtered result
    """

    def wrapper(*args, **kwargs):
        # if logger:
        #     logger.info("Begin function {0}".format(func.__name__))
        # else:
        #     print("Begin function {0}".format(func.__name__))
        return [s for s in func(*args, **kwargs) if check(s)]

    return wrapper


def print_zh_list(iterable):
    for i in iterable:
        print(i)


def save_model(model, path, name):
    """
    Save a sklearn model into a file.

    :param model: Scikit-learn model.

    :param path: File path.

    :param name: File name.

    :return: None.
    """
    from sklearn.externals import joblib
    joblib.dump(model, os.path.join(path, name))


def load_model(path, name):
    """
    Load a sklearn model.

    :param path: File path.

    :param name: File name.

    :return: The model object.
    """
    from sklearn.externals import joblib
    return joblib.load(os.path.join(path, name))


chinese_sentence_delimiters = "。；？！".decode("utf-8")
