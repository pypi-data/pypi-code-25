#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""

@version: 0.1
@author:  quantpy
@file:    debug.py
@time:    2018/4/19 14:28
"""

import sys


class ExceptionHook(object):
    instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            from IPython.core import ultratb
            self.instance = ultratb.FormattedTB(
                mode='Plain', color_scheme='Linux', call_pdb=1)
        return self.instance(*args, **kwargs)


sys.excepthook = ExceptionHook()
