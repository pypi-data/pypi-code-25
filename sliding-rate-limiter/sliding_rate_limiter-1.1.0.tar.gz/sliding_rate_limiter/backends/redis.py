# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from sliding_rate_limiter.backends.base import RateLimiterBackend


class RedisBackend(RateLimiterBackend):
    """
    Uses a Redis hash (dictionary) and a Lua script to implement the
    leaky bucket algorithm.
    """
    def __init__(
        self,
        connection
    ):
        self.connection = connection
        # ARGV[1] = limit_max
        # ARGV[2] = limit_window
        self._leak_and_increase_bucket = self.connection.register_script('''
redis.replicate_commands()
local now = redis.call('TIME')
local bucket = redis.call('HMGET', KEYS[1], 'time', 'height')
local delta = (now[1] - (bucket[1] or 0))
local decay = ARGV[1] / ARGV[2]
local height = math.max(0, (bucket[2] or 0) - delta * decay)
local full = math.ceil(height) >= tonumber(ARGV[1])
if (not full) then
    height = height + 1
end
redis.call('HMSET', KEYS[1], 'time', now[1], 'height', height)
redis.call('EXPIRE', KEYS[1], ARGV[2])
return full
''')

    def leak_and_increase_bucket(self, key, limit_max, limit_window):
        return self._leak_and_increase_bucket(keys=[key], args=[limit_max, limit_window]) == 1
