#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from .abstract_cache import AbstractCache
from .memcached_cache import MemcachedCache

log = logging.getLogger(__name__)

class NoneCache(AbstractCache):
    def __init__(self, cache_name):
        self._name = cache_name
        self._error = Exception("External CacheClient: Invalid cache type provided")

    def get(self, cache_key):
        return None, cache_key, self._error

    def put(self, cache_key, cache_value, expires_in):
        return cache_value, cache_key, self._error

    def delete(self, cache_key):
        return False, cache_key, self._error

    @property
    def obj(self):
        return None

    @property
    def err(self):
        return self._error

    @property
    def name(self):
        return self._name

    @property
    def cache_value_size_limit_in_bytes(self):
        return 0


CACHE_TYPES = {
    'Memcached': MemcachedCache,
}


def factoryCache(type_name, cache_name):
    cache_type = CACHE_TYPES.get(type_name, NoneCache)
    cache_obj = cache_type(cache_name)

    log.info(
        "Factory",
        extra={
            "type_name": type_name,
            "cache_name": cache_name,
            "cache_type": type(cache_type),
            "cache_obj": type(cache_obj)
        }
    )

    return cache_obj
