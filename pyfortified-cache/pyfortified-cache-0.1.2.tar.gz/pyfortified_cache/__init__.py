#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__title__ = 'pyfortified-cache'
__version__ = '0.1.2'
__version_info__ = tuple(__version__.split('.'))

__author__ = 'jeff00seattle'
__license__ = 'MIT License'
__copyright__ = 'Copyright 2018 jeff00seattle'


from .cache_types import CacheTypes
from .abstract_cache import AbstractCache
from .cache_factory import factoryCache
from .local_cache import (
    local_cache_get,
    local_cache_put,
    local_cache_delete,
)
from .cache_client import (
    create_cache_key,
    CacheClient,
)