# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import


from freezegun import freeze_time
import pytest

from sliding_rate_limiter.backends.proxy import ProxyBackend
from sliding_rate_limiter.backends.memory import MemoryBackend
from sliding_rate_limiter import UnconfiguredBackendError


def test_proxy_backend():
    backend = ProxyBackend()
    with pytest.raises(UnconfiguredBackendError):
        backend.leak_and_increase_bucket('foo', 1, 1)
    backend.proxy_to(MemoryBackend())

    with freeze_time('2000-01-01 00:00:00'):
        assert not backend.leak_and_increase_bucket('foo', 1, 1)
        assert backend.leak_and_increase_bucket('foo', 1, 1)
        assert backend.leak_and_increase_bucket('foo', 1, 1)

    with freeze_time('2000-01-01 00:00:01'):
        assert not backend.leak_and_increase_bucket('foo', 1, 1)
        assert backend.leak_and_increase_bucket('foo', 1, 1)

        # new backend, so should reset
        backend.proxy_to(MemoryBackend())
        assert not backend.leak_and_increase_bucket('foo', 1, 1)
        assert backend.leak_and_increase_bucket('foo', 1, 1)
