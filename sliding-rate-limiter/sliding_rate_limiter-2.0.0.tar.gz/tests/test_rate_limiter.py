# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from freezegun import freeze_time
import pytest

from sliding_rate_limiter.backends.memory import MemoryBackend
from sliding_rate_limiter.rate_limited_function import RateLimitedFunction, RateLimitExceededError
from sliding_rate_limiter.utils import function_key_generator


def dummy(a=1):
    pass


def test_rate_limiter():
    backend = MemoryBackend()
    limited = RateLimitedFunction(dummy, '2/s', function_key_generator(dummy), backend)
    with freeze_time('2000-01-01 00:00:00'):
        limited()
        limited()
        with pytest.raises(RateLimitExceededError):
            limited()
        with pytest.raises(RateLimitExceededError):
            limited()
        limited(2)
        limited(2)
        with pytest.raises(RateLimitExceededError):
            limited(2)
    with freeze_time('2000-01-01 00:00:00.5'):
        limited()
        with pytest.raises(RateLimitExceededError):
            limited()
        limited(2)
        with pytest.raises(RateLimitExceededError):
            limited(2)
    with freeze_time('2000-01-01 00:00:01'):
        limited()
        with pytest.raises(RateLimitExceededError):
            limited()
        limited(2)
        with pytest.raises(RateLimitExceededError):
            limited(2)
    with freeze_time('2000-01-01 00:00:02'):
        limited()
        limited()
        with pytest.raises(RateLimitExceededError):
            limited()
        limited(2)
        limited(2)
        with pytest.raises(RateLimitExceededError):
            limited(2)
