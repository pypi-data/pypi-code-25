#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from pymemcache_client import PymemcacheClient

from .abstract_cache import AbstractCache
from .cache_types import CacheTypes
from .errors import get_exception_message
from .constants import SECONDS_FOR_30_MINUTES

log = logging.getLogger(__name__)


class MemcachedCache(AbstractCache):
    """
    Using https://github.com/pinterest/pymemcache
    """

    _MEMCACHED_MAX_SIZE = 1000000
    _MEMCACHED_MAX_SIZE_FRACTION_LIMIT = 0.2

    @property
    def cache_value_size_limit_in_bytes(self):
        return self._MEMCACHED_MAX_SIZE*self._MEMCACHED_MAX_SIZE_FRACTION_LIMIT

    @property
    def cache_type(self):
        return self._cache_type
    @cache_type.setter
    def cache_type(self, value):
        self._cache_type = value

    @property
    def cache_client(self):
        return self._memcached_client
    @cache_client.setter
    def cache_client(self, value):
        self._memcached_client = value

    @property
    def cache_error(self):
        return self._memcached_error
    @cache_error.setter
    def cache_error(self, value):
        self._memcached_error = value

    @property
    def cache_name(self):
        return self._key_prefix
    @cache_name.setter
    def cache_name(self, value):
        self._key_prefix = value

    def __init__(self, cache_name):
        self.cache_type = CacheTypes.MEMCACHED_CACHE
        self.cache_name = cache_name

        log.debug(
            "{0}: Init: 'cache_name': '{1}'".format(
                self.cache_type,
                self.cache_name
            )
        )

        self.cache_error = None

        # Using pymemcache.json for configuring instance of PymemcacheClient.
        pymemcache_client = PymemcacheClient()
        self.cache_client = None if pymemcache_client is None else pymemcache_client.cache_client

        if self.cache_client is None:
            log.debug(
                "{0}: INIT: 'cache_name': '{1}': not created".format(
                    self.cache_type,
                    self.cache_name
                )
            )
        else:
            log.debug(
                "{0}: INIT: 'cache_name': '{1}': created".format(
                    self.cache_type,
                    self.cache_name
                )
            )

    def gen_memcached_key(self, key):
        # return "{}.{}".format(self._key_prefix, key)
        return key

    def get(self, cache_key, request_label=None):
        if self._memcached_client is None:
            raise ValueError(error_message="No cache provided")
        if cache_key is None:
            raise ValueError(error_message="No cache_key provided")

        cache_error = None
        memcached_key = self.gen_memcached_key(cache_key)

        log.debug(
            "{0}: GET: 'cache_key': '{1}' in 'cache_name': '{2}', label: '{3}'".format(
                self.cache_type,
                memcached_key,
                self.cache_name,
                request_label
            )
        )

        if self.cache_client is None:
            raise ValueError(
                error_message="{0}: GET: Error: Undeclared CacheClient".format(self.cache_type)
            )

        try:
            cache_value_get = self.cache_client.get(memcached_key)
        except Exception as ex:
            raise Exception(
                error_message="{0}: GET: Error: '{1}'".format(self.cache_type, get_exception_message(ex)),
                errors=ex
            )

        if cache_value_get is not None:
            cache_value_get = self.cache_value_deserialize(cache_value_get)

        return cache_value_get, memcached_key, cache_error

    def put(self, cache_key, cache_value, expires_in=SECONDS_FOR_30_MINUTES, request_label=None):

        if self.cache_client is None:
            raise ValueError(error_message="No cache provided")
        if cache_key is None:
            raise ValueError(error_message="No cache_key provided")
        if cache_value is None:
            raise ValueError(error_message="No cache_value provided")

        cache_error = None

        cache_value = self.cache_value_serialize(cache_value)

        log.debug(
            "{0}: PUT: 'cache_value' '{1}' for 'cache_key': '{2}' in 'cache_name': '{3}', label: '{4}'".format(
                self.cache_type,
                cache_value,
                cache_key,
                self.cache_name,
                request_label
            )
        )

        if self.cache_client is None:
            raise ValueError(
                error_message="{0}: PUT: Error: Undeclared CacheClient".format(self.cache_type)
            )

        try:
            res = self.cache_client.set(
                key=self.gen_memcached_key(cache_key),
                value=cache_value,
                expire=expires_in,
            )
        except Exception as ex:
            raise Exception(
                error_message="{0}: PUT: Error: '{1}'".format(self.cache_type, get_exception_message(ex)),
                errors=ex
            )

        log.debug("{0}: PUT: Result: '{1}'".format(self.cache_type, res))

        return cache_value, cache_key, cache_error

    def delete(self, cache_key, request_label=None):
        if self.cache_client is None:
            raise ValueError(error_message="No cache provided")
        if cache_key is None:
            raise ValueError(error_message="No cache_key provided")

        cache_error = None
        memcached_key = self.gen_memcached_key(cache_key)

        log.debug(
            "{0}: DELETE: 'cache_key': '{1}', label: '{2}'".format(
                self.cache_type,
                memcached_key,
                request_label
            )
        )

        if self.cache_client is None:
            raise ValueError(
                error_message="{0}: DELETE: Error: Undeclared CacheClient".format(self.cache_type)
            )

        try:
            cache_delete_success = self.cache_client.delete(memcached_key)
        except Exception as ex:
            raise Exception(
                error_message="{0}: DELETE: Error: {1}".format(self.cache_type, get_exception_message(ex)),
                errors=ex
            )

        return cache_delete_success, memcached_key, cache_error


def main():
    mc = MemcachedCache('test')
    value = {
        'type': 'cost',
        'version': 1
    }
    mc.put('key', value)
    print(mc.get('key'))
    mc.delete('key')
    print(mc.get('key'))


if __name__ == '__main__':
    main()
