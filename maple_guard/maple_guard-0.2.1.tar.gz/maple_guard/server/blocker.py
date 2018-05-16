# -*- coding: utf-8 -*-

import time


class Blocker(object):

    rds = None

    def __init__(self, rds):
        self.rds = rds

    def is_blocked(self, key):
        return self.rds.get(key)

    def block(self, key, timeout):
        """
        只有key不存在的时候，才重新设置，否则会导致block timeout一直延长
        :param key:
        :param timeout: 超时时间，<0 代表无限
        :return:
        """
        value = int(time.time())

        kwargs = dict(
            nx=True
        )

        if timeout >= 0:
            kwargs.update(dict(
                ex=timeout
            ))

        return self.rds.set(key, value, **kwargs)

    def unblock(self, key):
        return self.rds.delete(key)
