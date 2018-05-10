# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import


from .utils import parse_limit


class RateLimitedFunction(object):
    """
    Rate-limits the given function to ``limit`` frequency per key generated
    by ``key_generator`` from the arguments, using the given rate limiting ``backend``.

    This is usually used indirectly via
    ``sliding_rate_limiter.region.RateLimiterRegion.rate_limit_on_arguments()``.
    """
    def __init__(
        self,
        fn,
        limit,
        key_generator,
        backend
    ):
        self.fn = fn
        self.limit_max, self.limit_window = parse_limit(limit)
        self.key_generator = key_generator
        self.backend = backend

    def __call__(self, *args, **kwargs):
        full = self.backend.leak_and_increase_bucket(
            key=self.key_generator(*args, **kwargs),
            limit_max=self.limit_max,
            limit_window=self.limit_window
        )
        if full:
            raise RateLimitExceededError(self.limit_max, self.limit_window)
        return self.fn(*args, **kwargs)


class RateLimitExceededError(Exception):
    """
    Raised when a rate limit has been exceeded
    """
    def __init__(self, limit_max, limit_window):
        self.limit_max = limit_max
        self.limit_window = limit_window
        super(RateLimitExceededError, self).__init__(
            "Rate has exceeded limit (%s) in the past %sms" % (
                limit_max,
                limit_window
            )
        )
