# -*- coding: utf-8 -*-


class RateLimiter(object):

    rds_extend = None

    def __init__(self, rds_extend):
        """
        :param rds_extend: redis extend
        :return:
        """
        self.rds_extend = rds_extend

    def hit(self, key, limit_params, times=1):
        """
        :param key:
        :param limit_params: 频率限制，格式: [(max_times, duration), ]
            max_times: 次数, -1代表无限，压根就不用处理了
            duration: 多长时间内的计算，必须>=0
        :param times: 次数
        :return: 被限制住的数据 [(max_times, duration)]
        """
        limited_values = []

        for max_times, duration in limit_params or []:
            if max_times < 0:
                # 无需判断
                continue

            # 要带上duration，否则互相会冲突
            real_key = '%s#%s/%s' % (key, max_times, duration)

            if self.rds_extend.limit_incrby(real_key, times, max_times, duration):
                # 有一个超限，就是超限
                limited_values.append((max_times, duration))

        return limited_values
