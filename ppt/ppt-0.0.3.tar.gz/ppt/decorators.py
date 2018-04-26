#!/usr/local/bin/python3

import time
from ppt.profiler import Profiler
from functools import wraps


def timeit(fn):
    @wraps(fn)
    def measure_time(*args, **kwargs):
        start = time.time()
        res = fn(*args, **kwargs)
        end = time.time()
        name = fn.func_name
        print("@timeit: " + name + " took " + str(end - start) + " seconds")
        return res
    return measure_time


def cprofile(fn):
    @wraps(fn)
    def measure_perf(*args, **kwargs):
        prof = Profiler()
        prof.start()
        res = fn(*args, **kwargs)
        prof.stop()
        prof.score()
        return res
    return measure_perf
