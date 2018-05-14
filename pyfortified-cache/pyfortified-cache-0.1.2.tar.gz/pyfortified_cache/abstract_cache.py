#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ujson as json
from .errors import get_exception_message

class CacheMethodNotImplementedError(object):
    def __init__(self, class_obj, method_obj):
        raise NotImplementedError(
            "{class_name} object does not implement the method {method_name}".format(
                class_name=class_obj.__name__,
                method_name=method_obj.__name__,
            )
        )

class AbstractCache(object):
    def __init__(self, cache_name):
        raise CacheMethodNotImplementedError(self.__class__, self.__init__)

    def get(self, cache_key, request_label=None):
        raise CacheMethodNotImplementedError(self.__class__, self.get)

    def put(self, cache_key, cache_value, expires_in, request_label=None):
        raise CacheMethodNotImplementedError(self.__class__, self.put)

    def delete(self, cache_key, request_label=None):
        raise CacheMethodNotImplementedError(self.__class__, self.delete)

    @property
    def cache_type(self):
        raise CacheMethodNotImplementedError(self.__class__, self.cache_type)

    @property
    def cache_client(self):
        raise CacheMethodNotImplementedError(self.__class__, self.cache_client)

    @property
    def cache_error(self):
        raise CacheMethodNotImplementedError(self.__class__, self.cache_error)

    @property
    def cache_name(self):
        raise CacheMethodNotImplementedError(self.__class__, self.cache_name)

    @property
    def cache_value_size_limit_in_bytes(self):
        raise CacheMethodNotImplementedError(self.__class__, self.cache_value_size_limit_in_bytes)

    def cache_value_serialize(self, cache_value):
        if not (isinstance(cache_value, str) or isinstance(cache_value, dict) or isinstance(cache_value, list)):
            raise ValueError(
                error_message="Serialize: Invalid 'cache_value' type: '{}'".format(type(cache_value).__name__)
            )

        try:
            if isinstance(cache_value, dict):
                external_cache_value = json.dumps(cache_value, double_precision=15, sort_keys=True)
            elif isinstance(cache_value, list):
                external_cache_value = json.dumps(cache_value, double_precision=15)
            else:
                external_cache_value = cache_value
        except TypeError as type_ex:
            raise ValueError(error_message=get_exception_message(type_ex), errors=type_ex)
        except Exception as ex:
            raise

        if external_cache_value:
            if not isinstance(external_cache_value, str):
                raise Exception(
                    error_message="Serialize: cache value is not 'str'"
                )
            if len(external_cache_value) == 0:
                raise Exception(
                    error_message="Serialize: cache value is empty"
                )

        return external_cache_value

    def cache_value_deserialize(self, cache_value):
        try:
            cache_value = json.loads(cache_value)
        except ValueError as json_decode_ex:
            if isinstance(cache_value, str):
                cache_value = cache_value
            elif isinstance(cache_value, bytes):
                cache_value = cache_value.decode("utf-8")
            else:
                raise Exception(
                    error_message=get_exception_message(json_decode_ex),
                    errors=json_decode_ex
                )
        except Exception as ex:
            raise Exception(
                error_message=get_exception_message(ex), errors=ex
            )

        return cache_value

    def check_value_constraints(self, cache_value):
        # We do not want to keep "too large" values in cache
        cache_value_size = len(cache_value)
        if cache_value_size > self.cache_value_size_limit_in_bytes:
            raise ValueError(
                error_message="cache_value size ({}) is above predefined limitation {}.".format(
                    cache_value_size,
                    self.cache_value_size_limit_in_bytes,
                )
            )
