# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from sliding_rate_limiter.backends.base import RateLimiterBackend


class NullBackend(RateLimiterBackend):
    """
    Does nothing (does not rate limit)
    """
    def leak_and_increase_bucket(self, key, limit_max, limit_window):
        return False
