# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import abc

import six
import functools
from sliding_rate_limiter.utils import function_key_generator
from sliding_rate_limiter.rate_limited_function import RateLimitedFunction
from sliding_rate_limiter.backends import ProxyBackend


class RateLimiterRegion(six.with_metaclass(abc.ABCMeta, object)):
    """
    A region (similar to a dogpile.cache region) containing
    configuration for the rate limiter backend, key generator,
    namespace, etc.

    Usage is like:

    @region.rate_limit_with_arguments(limit='5/s')
    def foo():
        pass
    """

    def __init__(
        self,
        name='default',
        namespace=None,
        function_key_generator=function_key_generator,
    ):
        self.name = name
        self.namespace = namespace
        self.function_key_generator = function_key_generator
        self.proxy_backend = ProxyBackend()

    def configure(self, backend):
        self.proxy_backend.proxy_to(backend)

    def rate_limit_with_arguments(
        self,
        limit,
        namespace=None,
        function_key_generator=None,
        to_str=six.text_type
    ):
        namespace = namespace or self.namespace
        function_key_generator = function_key_generator or self.function_key_generator

        def limiter(fn):
            key_generator = function_key_generator(fn, namespace, to_str=to_str)
            return functools.wraps(fn)(RateLimitedFunction(
                fn,
                limit,
                key_generator=key_generator,
                backend=self.proxy_backend
            ))

        return limiter


class RateLimitExceededError(Exception):
    """
    Raised when a rate limit has been exceeded
    """
    def __init__(self, limit):
        pass
