# -*- coding: utf-8 -*-

"""Top-level package for sliding-rate-limiter."""

__author__ = """Kalibrr Technology Ventures, Inc."""
__email__ = 'hirenow@kalibrr.com'
__version__ = '2.1.0'

from .rate_limited_function import RateLimitExceededError  # noqa
from .backends.proxy import UnconfiguredBackendError  # noqa
