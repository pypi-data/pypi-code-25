# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

"""
In order for these tests to work, there must be a redis server
running and listening at 127.0.0.1:6379
"""

import time

import pytest

redis = pytest.importorskip('redis')

from sliding_rate_limiter.backends.redis import RedisBackend


@pytest.mark.redis
def test_redis_backend():
    conn = redis.StrictRedis('127.0.0.1')
    backend = RedisBackend(conn)
    assert not backend.leak_and_increase_bucket('foo', 1, 1)
    assert backend.leak_and_increase_bucket('foo', 1, 1)
    assert backend.leak_and_increase_bucket('foo', 1, 1)
    time.sleep(1)
    assert not backend.leak_and_increase_bucket('foo', 1, 1)
    assert backend.leak_and_increase_bucket('foo', 1, 1)
