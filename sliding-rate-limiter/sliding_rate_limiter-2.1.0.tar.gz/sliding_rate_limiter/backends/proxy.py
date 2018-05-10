# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from sliding_rate_limiter.backends.base import RateLimiterBackend


class ProxyBackend(RateLimiterBackend):
    """
    Proxies to another backend
    """
    def __init__(self, backend=None):
        self.backend = backend

    def proxy_to(self, backend):
        self.backend = backend

    def leak_and_increase_bucket(self, key, limit_max, limit_window):
        try:
            return self.backend.leak_and_increase_bucket(key, limit_max, limit_window)
        except AttributeError:
            raise UnconfiguredBackendError("Please configure a backend first")


class UnconfiguredBackendError(Exception):
    pass
