# -*- coding: utf-8 -*-

"""
股票池对象 - 动态增减
=======================================================================================
"""


class StockPool:
    def __init__(self):
        self.pool = set()

    def add(self, stocks):
        """添加股票(支持添加多只股票)

        params
        ---------
        stocks      list or tuple
        """
        raise NotImplementedError

    def remove(self, stocks):
        """删除股票(支持删除多只股票)

        params
        ---------
        stocks      list or tuple
        """
        raise NotImplementedError

    def empty(self):
        """清空股票池"""
        raise NotImplementedError

    def is_empty(self):
        """判断股票池是否为空"""
        raise NotImplementedError

