#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class CacheTypes(object):
    """Cache Types ENUM
    """
    UNDEFINED = None
    MEMCACHED_CACHE = 'Memcached'

    @staticmethod
    def validate(cache_type):
        return cache_type in [
            CacheTypes.MEMCACHED_CACHE,
        ]