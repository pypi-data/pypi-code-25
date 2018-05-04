# -*- coding: utf-8 -*-
""" Handle utility objects. """
import logging
import math
import time

logger = logging.getLogger(__name__)


def timeit(func=None, loops=1, verbose=False):
    """
    Provides timing for a function and the ability to run multiple times.

    Args:
      func (): the function to time
      loops (): number of times to run the function
      verbose (): display detailed info

    Returns:
      Nothing
    """
    if func is not None:
        def inner(*args, **kwargs):
            sums = 0.0
            mins = 1.7976931348623157e+308
            maxs = 0.0
            logger.info('====%s Timing====' % func.__name__)
            for i in range(0, loops):
                t0 = time.time()
                result = func(*args, **kwargs)
                dt = time.time() - t0
                mins = dt if dt < mins else mins
                maxs = dt if dt > maxs else maxs
                sums += dt
                if verbose:
                    logger.info('\t%r ran in %2.9f sec on run %s' % (func.__name__, dt, i))
            logger.info('%r min run time was %2.9f sec' % (func.__name__, mins))
            logger.info('%r max run time was %2.9f sec' % (func.__name__, maxs))
            logger.info('%r avg run time was %2.9f sec in %s runs' % (func.__name__, sums / loops, loops))
            logger.info('==== end ====')
            return result

        return inner
    else:
        def partial_inner(a_function):
            return timeit(a_function, loops, verbose)

        return partial_inner


# Retry decorator with exponential backoff
def retry(tries, exceptions=Exception, delay=3, backoff=2):
    """
    Retries a function or method if exception is raised.
    delay sets the initial delay in seconds, and backoff sets the factor by which
    the delay should lengthen after each failure. backoff must be greater than 1,
    or else it isn't really a backoff. tries must be at least 0, and delay
    greater than 0.
    """

    if backoff <= 1:
        raise ValueError("backoff must be greater than 1")

    tries = math.floor(tries)
    if tries < 0:
        raise ValueError("tries must be 0 or greater")

    if delay <= 0:
        raise ValueError("delay must be greater than 0")

    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay  # make mutable
            completed = False

            while not completed:
                try:
                    return f(*args, **kwargs)
                except exceptions:
                    if not mtries:
                        logger.error("No retries left")
                        raise
                    mtries -= 1  # consume an attempt
                    logger.debug("Attempt failed, retrying in {} secs. ({} retries left)".format(
                        int(mdelay),
                        int(mtries)
                    ))
                    time.sleep(mdelay)  # wait...
                    mdelay *= backoff  # make future wait longer

        return f_retry  # true decorator -> decorated function

    return deco_retry  # @retry(arg[, ...]) -> true decorator
