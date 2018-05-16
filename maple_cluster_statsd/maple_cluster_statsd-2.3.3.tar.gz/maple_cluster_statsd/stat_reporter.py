# -*- coding: utf-8 -*-

"""
读取gateway统计数据，并上报数据至statsd
"""

from .stat_reader import StatReader


class StatReporter(object):

    # 需要上报gauge的
    gauge_stat_list = None
    # 需要上报incr的
    incr_stat_list = None

    stat_reader = None
    statsd_client = None
    statsd_prefix = None

    # 统计上报时的命名转化
    statsd_name_converter = None

    # 上次的stat_reader的结果
    last_stat_result = None

    def __init__(self, cmd, statsd_client, gauge_stat_list, incr_stat_list, statsd_name_converter=None):
        """
        :param cmd: 命令
        :param statsd_client: statsd_client
        :param gauge_stat_list: 值类型的统计列表
        :param incr_stat_list: 计数类型的统计列表
        :param statsd_name_converter: statsd统计上报名字转换函数
        :return:
        """

        self.stat_reader = StatReader(cmd)
        self.statsd_client = statsd_client
        self.gauge_stat_list = gauge_stat_list
        self.incr_stat_list = incr_stat_list
        # 默认是不变
        self.statsd_name_converter = statsd_name_converter or (lambda x: x)

    def report(self):
        """
        上报
        :return:
        """

        result = self.stat_reader.read()

        if not result:
            return False

        for local_stat_name in self.gauge_stat_list:
            remote_stat_name = self.statsd_name_converter(local_stat_name)
            value = result.get(local_stat_name, 0)

            self.statsd_client.gauge(remote_stat_name, value)

        if self.last_stat_result is not None:
            for local_stat_name in self.incr_stat_list:
                remote_stat_name = self.statsd_name_converter(local_stat_name)
                value = result.get(local_stat_name, 0) - self.last_stat_result.get(local_stat_name, 0)

                self.statsd_client.incr(remote_stat_name, value)

        self.last_stat_result = result

        return True
