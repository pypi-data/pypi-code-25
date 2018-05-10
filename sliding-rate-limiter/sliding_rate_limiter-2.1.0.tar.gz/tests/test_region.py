# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
import six
from freezegun import freeze_time

from sliding_rate_limiter.backends.memory import MemoryBackend
from sliding_rate_limiter.rate_limited_function import RateLimitExceededError
from sliding_rate_limiter.region import RateLimiterRegion


def test_rate_limiter_region():
    region = RateLimiterRegion('foo')

    def dummy(*args, **kwargs):
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

    limited = region.rate_limit_with_arguments(
        '1/s', partial_key_generator=lambda *args: six.text_type(args[0])
    )(dummy)
    with freeze_time('2000-01-01 00:00:00'):
        limited(1, 2)
        with pytest.raises(RateLimitExceededError):
            limited(1, 3)
        limited(2, 2)
    with freeze_time('2000-01-01 00:00:01'):
        limited(1, 4)
        with pytest.raises(RateLimitExceededError):
            limited(1, 5)
        limited(2, 1)
