# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import threading
import time
import math

from sliding_rate_limiter.backends.base import RateLimiterBackend


class _DummyLock(object):
    def acquire(self):
        pass

    def release(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self):
        pass


_dummy_lock = _DummyLock()


class MemoryBackend(RateLimiterBackend):
    """
    Uses an in-memory leaky bucket to implement the leaky-bucket algorithm.
    If ``threadsafe`` is True, this uses a `threading.Lock` to make the modifications atomic.
    """
    def __init__(
        self,
        threadsafe=True
    ):
        self.buckets = {}
        self.threadsafe = threadsafe
        if threadsafe:
            self.overall_lock = threading.Lock()
        else:
            self.overall_lock = _dummy_lock

    def leak_and_increase_bucket(self, key, limit_max, limit_window):
        with self.overall_lock:
            if key not in self.buckets:
                self.buckets[key] = {
                    'lock': threading.Lock() if self.threadsafe else _dummy_lock,
                    'time': 0,
                    'height': 0
                }
            bucket = self.buckets[key]

        with bucket['lock']:
            now = time.time()
            decay = limit_max / limit_window
            bucket['height'] = max(0, bucket['height'] - (now - (bucket['time'] or 0)) * decay)
            bucket['time'] = now
            full = math.ceil(bucket['height']) >= limit_max
            if not full:
                bucket['height'] += 1
        return full
