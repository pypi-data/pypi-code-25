# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from freezegun import freeze_time
import pytest

from sliding_rate_limiter.region import RateLimiterRegion
from sliding_rate_limiter.backends.memory import MemoryBackend
from sliding_rate_limiter.rate_limited_function import RateLimitExceededError


def test_rate_limiter_region():
    region = RateLimiterRegion('foo')

    def dummy():
        pass

    limited = region.rate_limit_with_arguments('1/s')(dummy)
    region.configure(MemoryBackend())
    with freeze_time('2000-01-01 00:00:00'):
        limited()
        with pytest.raises(RateLimitExceededError):
            limited()
    with freeze_time('2000-01-01 00:00:01'):
        limited()
        with pytest.raises(RateLimitExceededError):
            limited()
