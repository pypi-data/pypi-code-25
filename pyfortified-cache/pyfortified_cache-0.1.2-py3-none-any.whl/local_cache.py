#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def local_cache_get(cache, cache_key, cache_group_name=None):
    if cache is None:
        return None, None

    cache_group = cache.get(cache_group_name, None)

    if cache_group is None:
        return None, cache_key

    cache_value = cache_group.get(cache_key, None)

    return cache_value, cache_key


def local_cache_put(cache, cache_key, cache_value, cache_group_name):
    if cache_group_name not in cache:
        cache[cache_group_name] = {}

    cache[cache_group_name].update({cache_key: cache_value})


def local_cache_delete(cache, cache_key, cache_group_name=None):
    cache_value = cache[cache_group_name].pop(cache_key, None)
    return cache_value is not None
