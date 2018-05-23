#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: manager.py
@time: 22/05/2018 16:03
"""


class CacheManager(object):
    def __init__(self, cfg):
        self._cfg = cfg
        self._stores = {}

    def store(self, name):
        if name in self._stores:
            return self._stores[name]