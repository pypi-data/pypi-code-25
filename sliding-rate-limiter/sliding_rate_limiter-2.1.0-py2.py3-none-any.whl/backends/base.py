# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import


import abc

import six


class RateLimiterBackend(six.with_metaclass(abc.ABCMeta, object)):
    """
    A backend that implements an atomic ``leak_and_increase_bucket``.
    """
    def leak_and_increase_bucket(self, key, limit_max, limit_window):
        """
        Leaks the bucket with the given key (and initializes one if needed) based on the given
        ``limit_max`` (maximum height of bucket) and ``limit_window`` (duration in seconds over which
        ``limit_max`` leaks out), and then increases the bucket.

        .. note:

            The bucket does not increase above its maximum (i.e., failed operations
            do not count against the limit).

        :return: whether the bucket is too full (i.e., rate limit exceeded) or not
        """
        raise NotImplementedError()
