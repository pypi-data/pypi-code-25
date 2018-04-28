#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""

@version: 0.1
@author:  quantpy
@file:    decorators.py
@time:    2018/4/28 9:25
"""
import sys
from functools import wraps, partial
import warnings
from datetime import datetime
import reprlib

from .utils import get_full_parameters


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
                parameter_args = reprlib.repr(', '.join(repr(arg) for arg in args_))[1:-1]
                parameter_kwargs = reprlib.repr(', '.join(f'{k}={v!r}' for k, v in kwargs_.items()))[1:-1]
                parameters = parameter_args
                if parameters:
                    if parameter_kwargs:
                        parameters = ', '.join([parameters, parameter_kwargs])
                else:
                    parameters = parameter_kwargs

                printf(f'Running {func.__name__}({parameters})')

            ret = func(*args, **kwargs)

            time_end = datetime.now()
            if level >= 1:
                printf(time_end, func.__name__, 'finished.')
            printf('Total time used: {!s}\n'.format(time_end - time_start))

            return ret
        return wrapper
    return timer_


def handle_exceptions(*exc_types, handler=None):
    """忽略但警告指定异常"""
    def wrapper_(func):
        @wraps(func)
        def wrapper__(*args, **kwargs):
            try:
                ret = func(*args, **kwargs)
            except BaseException as e:
                if isinstance(e, exc_types):
                    if callable(handler):
                        handler(e)
                    else:
                        warnings.warn(repr(e))
                    ret = None
                else:
                    raise e
            return ret
        return wrapper__
    return wrapper_


def filter_warnings(*warning_types, action='ignore'):
    """过滤指定警告类型，如果不指定将过滤所有警告"""
    def wrapper_(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with warnings.catch_warnings():
                if warning_types:
                    for warning_type in warning_types:
                        warnings.simplefilter(action, category=warning_type, append=True)
                else:
                    warnings.simplefilter(action, append=True)
                ret = func(*args, **kwargs)
            return ret
        return wrapper
    return wrapper_

