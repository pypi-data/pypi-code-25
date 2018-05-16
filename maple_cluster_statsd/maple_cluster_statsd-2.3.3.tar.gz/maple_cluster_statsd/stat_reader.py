# -*- coding: utf-8 -*-
"""
读取gateway统计数据并解析
"""

import os


class StatReader(object):

    cmd = None

    def __init__(self, cmd):
        """
        :param cmd: 统计命令
        :return:
        """
        self.cmd = cmd

    def read(self):
        """
        读取一次
        :return:
        """

        result = dict()

        for line in os.popen(self.cmd):
            values = line.split(':')
            if len(values) == 2:
                result[values[0].strip()] = int(values[1].strip())

        return result
