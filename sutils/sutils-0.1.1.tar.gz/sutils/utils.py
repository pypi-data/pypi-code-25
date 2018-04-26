#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""

@version: 0.1
@author:  quantpy
@file:    utils.py
@time:    2018/4/13 15:46
"""
import sys
from functools import wraps, partial
from datetime import datetime
import inspect
import reprlib


def timeit(func):
    """
    timing decorator
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        time_start = datetime.now()
        print(time_start, func.__name__, 'starts...')
        ret = func(*args, **kwargs)
        time_end = datetime.now()
        print(time_end, func.__name__, 'finished.')
        print('Total time used: {!s}'.format(time_end - time_start), '\n')

        return ret

    return wrapper


def timer(level=1, file=sys.stdout):
    def timer_(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            printf = partial(print, file=file)
            time_start = datetime.now()
            if level >= 1:
                printf(time_start, func.__name__, 'starts...')
            if level >= 2:
                args_, kwargs_, _ = get_full_parameters(func, *args, **kwargs)
                parameter_args = reprlib.repr(', '.join(repr(arg) for arg in args_))
                parameter_kwargs = reprlib.repr(', '.join(f'{k}={v!r}' for k, v in kwargs_.items()))
                parameters = ', '.join([parameter_args, parameter_kwargs])
                printf(f'Running {func.__name__}({parameters})')

            ret = func(*args, **kwargs)

            time_end = datetime.now()
            if level >= 1:
                printf(time_end, func.__name__, 'finished.')
            printf('Total time used: {!s}\n'.format(time_end - time_start))

            return ret
        return wrapper
    return timer_


def get_full_parameters(func, *args, **kwargs):
    """
    get full function parameters by
    given parameter and default parameter
    """
    sig = inspect.signature(func)
    sig_bind = sig.bind(*args, **kwargs)
    sig_bind.apply_defaults()
    return sig_bind.args, sig_bind.kwargs, sig_bind

