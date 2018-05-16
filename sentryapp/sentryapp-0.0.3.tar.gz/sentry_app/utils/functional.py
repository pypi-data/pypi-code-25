#coding: utf8
from __future__ import absolute_import


def curry(_curried_func, *args, **kwargs):
    def _curried(*moreargs, **morekwargs):
        return _curried_func(*(args+moreargs), **dict(kwargs, **morekwargs))
    _curried.__name__ = _curried_func.__name__
    _curried.func_name = _curried_func.func_name
    _curried.original_func = _curried_func
    return _curried



class cached_property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, type):
        res = instance.__dict__[self.func.__name__] = self.func(instance)
        return res
