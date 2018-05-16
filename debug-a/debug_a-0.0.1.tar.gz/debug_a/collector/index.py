# -*- coding: utf-8 -*-
"""
指数相关数据接口
==========================================
"""

import tushare as ts


def index_all():
    """指数行情接口"""
    return ts.get_index()

