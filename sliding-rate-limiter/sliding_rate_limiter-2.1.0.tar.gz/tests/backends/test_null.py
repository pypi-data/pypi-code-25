# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import


from freezegun import freeze_time

from sliding_rate_limiter.backends.null import NullBackend


def test_null_backend():
    backend = NullBackend()
    with freeze_time('2000-01-01 00:00:00'):
        assert not backend.leak_and_increase_bucket('foo', 1, 1)
        assert not backend.leak_and_increase_bucket('foo', 1, 1)
        assert not backend.leak_and_increase_bucket('foo', 1, 1)
