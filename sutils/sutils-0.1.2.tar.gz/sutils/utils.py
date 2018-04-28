#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""

@version: 0.1
@author:  quantpy
@file:    utils.py
@time:    2018/4/13 15:46
"""
import inspect


def get_full_parameters(func, *args, **kwargs):
    """
    get full function parameters by
    given parameter and default parameter
    """
    sig = inspect.signature(func)
    sig_bind = sig.bind(*args, **kwargs)
    sig_bind.apply_defaults()
    return sig_bind.args, sig_bind.kwargs, sig_bind

