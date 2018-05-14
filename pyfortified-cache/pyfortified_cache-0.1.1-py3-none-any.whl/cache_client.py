#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import json as json  # Do not convert to ujson
import types
from datetime import datetime
import traceback

from .utils import create_hash_key
from .cache_types import CacheTypes
from .cache_factory import factoryCache
from .local_cache import local_cache_get, local_cache_put, local_cache_delete
from .errors import get_exception_message
from .constants import SECONDS_FOR_30_MINUTES

# from pprintpp import pprint

log = logging.getLogger(__name__)


def create_cache_key(request_params=None, request_url=None, cache_group_name=None, client_unique_hash=None):
    """Create CacheClient Key

    Args:
        request_params:
        request_url:
        cache_group_name:
        client_unique_hash:

    Returns:

    """
    assert request_url or request_params or client_unique_hash

    cache_key_str = ''

    if cache_group_name:
        cache_key_str += cache_group_name + '-'

    if client_unique_hash:
        cache_key_str += client_unique_hash + '-'

    if request_params:
        assert isinstance(request_params, dict)
        cache_key_str += json.dumps(request_params, sort_keys=True)

    if request_url:
        cache_key_str += request_url

    assert cache_key_str
    assert len(cache_key_str) > 0

    cache_key = create_hash_key(key=cache_key_str)

    return cache_key


def create_cache_metrics_group():
    return {
        'external_cache': {
            'hit': 0,
            'miss': 0,
            'delete': 0,
            'put': {},
        },
        'local_cache': {
            'hit': 0,
            'miss': 0,
            'delete': 0,
            'put': 0,
        }
    }


class CacheClient(object):
    """Cache Client"""
    _external_cache = None
    _cache_name = None
    _local_cache = {}

    _cache_metrics = {}
    _client_unique_hash = None

    _cache_type = CacheTypes.UNDEFINED

    @property
    def cache_name(self):
        return self._cache_name
    @cache_name.setter
    def cache_name(self, value):
        self._cache_name = value

    @property
    def cache_type(self):
        return self._cache_type
    @cache_type.setter
    def cache_type(self, value):
        self._cache_type = value

    @property
    def external_cache(self):
        return self._external_cache
    @external_cache.setter
    def external_cache(self, value):
        self._external_cache = value

    def __init__(
        self,
        cache_name,
        cache_required=False,
        client_unique_hash=None,
        cache_type=CacheTypes.MEMCACHED_CACHE
    ):
        """CacheClient

        Args:
            cache_name: str, CacheClient group name
            cache_required: bool, Is caching required?
            client_unique_hash:
        """
        if not CacheTypes.validate(cache_type):
            raise ValueError("Parameter 'cache_type' is invalid: {0}".format(cache_type))
        if not cache_name:
            raise ValueError("Parameter 'cache_name' is invalid: {0}".format(cache_name))

        self.cache_type = cache_type
        self.cache_name = cache_name
        self._client_unique_hash = client_unique_hash

        log.info(
            "CacheClient: {0}: INIT".format(self.cache_type),
            extra={
                'cache_name': cache_name,
                'cache_required': cache_required,
                'client_unique_hash': client_unique_hash,
            },
        )

        self.external_cache = factoryCache(self.cache_type, self.cache_name)
        log.info(
            "CacheClient: {0}: DETAILS".format(self.cache_type),
            extra={"variables": vars(self.external_cache), "properties": dir(self.external_cache)}
        )

        if self.external_cache.cache_client is None and cache_required is True:
            log.error(
                "CacheClient: {0}: Error: Could not create cache. Maybe configuration is missing?".format(
                    self.cache_type
                ),
                extra={
                    'error': self.external_cache.err,
                    'cache_name': cache_name,
                },
            )
            raise Exception(
                "CacheClient: {0}: Error: CacheClient Required Set and cache create failed".format(
                    self.cache_type
                )
            )

    def get(
        self,
        cache_key=None,
        request_params=None,
        request_url=None,
        cache_group_name='default',
        request_label=None,
        local_only=False,
    ):
        """Get cache value

        Args:
            cache_key:
            request_params:
            request_url:
            cache_group_name:
            request_label:
            local_only:

        Returns:

        """
        if request_params is None:
            request_params = {}

        if cache_key is None:
            cache_key = create_cache_key(
                request_params,
                request_url,
                cache_group_name,
                client_unique_hash=self._client_unique_hash
            )

        if cache_key is None:
            raise ValueError(error_message="Undefined 'cache_key'")

        log.debug(
            "CacheClient: {0}: GET: Start".format(self.cache_type),
            extra={
                'cache_group_name': cache_group_name,
                'request_params': request_params,
                'request_url': request_url,
                'request_label': request_label,
                'cache_key': cache_key,
                'local_only': local_only
            }
        )

        if cache_group_name not in self._cache_metrics:
            self._cache_metrics[cache_group_name] = create_cache_metrics_group()

        cache_value, local_cache_key = local_cache_get(
            self._local_cache,
            cache_key=cache_key,
            cache_group_name=cache_group_name,
        )

        if cache_key:
            # validating the expected cache key should be the same
            # as the generated local cache key.
            assert cache_key == local_cache_key

        if cache_value:
            log.debug(
                "CacheClient: {0}: GET: Found".format(self.cache_type),
                extra={
                    'cache_group_name': cache_group_name,
                    'cache_key': cache_key,
                    'local_only': local_only
                }
            )
            self._cache_metrics[cache_group_name]['local_cache']['hit'] += 1
            return cache_value, local_cache_key

        log.debug(
            "CacheClient: {0}: GET: Not Found".format(self.cache_type),
            extra={
                'cache_group_name': cache_group_name,
                'cache_key': cache_key,
                'local_only': local_only
            }
        )

        # pprint(dir(self.external_cache))
        # pprint(vars(self.external_cache))

        self._cache_metrics[cache_group_name]['local_cache']['miss'] += 1

        if local_only is False and self.external_cache.cache_client is None:
            log.warning(
                "CacheClient: {0}: GET: No CacheClient Available".format(self.cache_type),
                extra={
                    'error': self.external_cache.cache_error
                }
            )

        # Bail early if we do not have an external cache to fallthrough to
        if self.external_cache.cache_client is None or local_only:
            log.debug(
                "CacheClient: Local: GET: Returned",
                extra={
                    'cache_type': self.cache_type,
                    'cache_group_name': cache_group_name,
                    'cache_key': cache_key,
                    'cache_value_size': sys.getsizeof(cache_value),
                    'local_only': local_only
                }
            )
            return cache_value, cache_key

        timer_start = datetime.now()
        cache_error = None
        external_cache_key = None

        try:
            cache_value, external_cache_key, cache_error = self.external_cache.get(cache_key, request_label)
        except (AttributeError, AssertionError) as ex:
            _, _, tb = sys.exc_info()
            traceback.print_tb(tb)  # Fixed format
            tb_info = traceback.extract_tb(tb)
            filename, line, func, text = tb_info[-1]

            raise Exception(
                error_message="CacheClient '{cache_type}': GET: Error occurred on file '{filename}', line '{line}', func '{func}', statement '{text}'".format(
                    cache_type=self.cache_type,
                    filename=filename,
                    line=line,
                    func=func,
                    text=text
                ),
                errors=ex,
                error_details=get_exception_message(ex)
            )

        except Exception as ex:
            log.error(
                "CacheClient: {0}: GET: Module Error: '{1}'".format(self.cache_type, ex.error_message),
                extra={
                    'cache_group_name': cache_group_name,
                    'cache_name': self.external_cache.cache_name,
                    'request_label': request_label,
                    'cache_key': cache_key,
                }
            )
            log.error("Do not abort. Continue without querying external cache.")
        except Exception as ex:
            log.error(
                "CacheClient: {0}: GET: Unexpected Error: '{1}'".format(self.cache_type, str(ex)),
                extra={
                    'cache_group_name': cache_group_name,
                    'cache_name': self.external_cache.cache_name,
                    'request_label': request_label,
                    'cache_key': cache_key,
                },
            )
            raise Exception(
                error_message="CacheClient: {0}: GET: Unexpected Error".format(
                    self.cache_type
                ),
                errors=ex,
                error_details=get_exception_message(ex)
            )

        timer_delta = datetime.now() - timer_start

        if cache_value is None:
            log.debug(
                "CacheClient: {0}: GET: Not Found".format(self.cache_type),
                extra={
                    'cache_group_name': cache_group_name,
                    'cache_key': cache_key,
                    'cache_error': cache_error,
                    'response_time_msecs': timer_delta.microseconds
                }
            )

            self._cache_metrics[cache_group_name]['external_cache']['miss'] += 1
            return None, external_cache_key

        log.debug(
            "CacheClient: {0}: GET: Found".format(self.cache_type),
            extra={
                'cache_group_name': cache_group_name,
                'cache_key': cache_key,
                'response_time_msecs': timer_delta.microseconds
            }
        )

        self._cache_metrics[cache_group_name]['external_cache']['hit'] += 1
        assert local_cache_key == external_cache_key

        local_cache_put(self._local_cache, cache_key, cache_value, cache_group_name)
        self._cache_metrics[cache_group_name]['local_cache']['put'] += 1

        log.debug(
            "CacheClient: {0}: GET: Completed".format(self.cache_type),
            extra={
                'cache_group_name': cache_group_name,
                'cache_key': cache_key,
                'cache_value_size': sys.getsizeof(cache_value)
            }
        )

        return cache_value, cache_key

    def put(
        self,
        cache_key,
        cache_value,
        cache_group_name='default',
        expires_in=SECONDS_FOR_30_MINUTES,
        request_label=None,
        local_only=False,
    ):
        """Put cache value

        Args:
            cache_key:
            cache_value:
            cache_group_name:
            expires_in:
            request_label:
            local_only:

        Returns:

        """
        if cache_key is None:
            raise ValueError(error_message="Undefined 'cache_key'")

        log.debug(
            "CacheClient: {0}: PUT: Start".format(self.cache_type),
            extra={
                'cache_group_name': cache_group_name,
                'request_label': request_label,
                'cache_key': cache_key,
                'local_only': local_only,
                'cache_value_size': sys.getsizeof(cache_value)
            }
        )

        if cache_group_name not in self._cache_metrics:
            self._cache_metrics[cache_group_name] = create_cache_metrics_group()

        local_cache_put(
            self._local_cache,
            cache_key,
            cache_value,
            cache_group_name,
        )
        self._cache_metrics[cache_group_name]['local_cache']['put'] += 1

        if local_only is False and self.external_cache.cache_client is None:
                log.warning(
                    "CacheClient: {0}: PUT: No CacheClient Available".format(self.cache_type),
                    extra={
                        'error': self.external_cache.cache_error
                    }
                )

        # Bail early if we do not have an external cache to fallthrough to
        if self.external_cache.cache_client is None or local_only:
            log.debug(
                "CacheClient: Local: PUT: Returned",
                extra={
                    'cache_type': self.cache_type,
                    'cache_group_name': cache_group_name,
                    'cache_key': cache_key,
                    'cache_value_size': sys.getsizeof(cache_value),
                    'local_only': local_only
                }
            )
            return

        timer_start = datetime.now()
        try:
            cache_value_put_response, cache_key, cache_error = self.external_cache.put(
                cache_key=cache_key,
                cache_value=cache_value,
                expires_in=expires_in,
                request_label=request_label
            )
        except Exception as ex:
            log.error(
                "CacheClient: {0}: PUT: Error: {1}".format(
                    self.cache_type,
                    ex.error_message,
                ),
                extra={
                    'cache_group_name': cache_group_name,
                    'cache_name': self.external_cache.cache_name,
                    'request_label': request_label,
                    'cache_key': cache_key,
                }
            )
            log.error("Do not abort. Continue without updating external cache.")
        except Exception as ex:
            log.error(
                "CacheClient: {0}: PUT: Error: {1}".format(
                    self.cache_type,
                    str(ex),
                ),
                extra={
                    'cache_group_name': cache_group_name,
                    'cache_name': self.external_cache.cache_name,
                    'request_label': request_label,
                    'cache_key': cache_key,
                },
            )
            raise Exception(
                error_message="CacheClient: {0}: PUT: Error: {1}".format(self.cache_type, get_exception_message(ex)),
                errors=ex,
                error_details=get_exception_message(ex),
            )

        timer_delta = datetime.now() - timer_start

        if expires_in not in self._cache_metrics[cache_group_name]['external_cache']['put']:
            self._cache_metrics[cache_group_name]['external_cache']['put'][expires_in] = 0
        self._cache_metrics[cache_group_name]['external_cache']['put'][expires_in] += 1

        log.debug(
            "CacheClient: {0}: PUT: Completed".format(self.cache_type),
            extra={
                'response_time_msecs': timer_delta.microseconds
            }
        )

    def delete(
        self,
        cache_key=None,
        cache_group_name='default',
        local_only=False,
        request_label=None,
    ):
        """Delete cache value

        Args:
            cache_key:
            cache_group_name:
            local_only:

        Returns:

        """
        if cache_group_name not in self._cache_metrics:
            self._cache_metrics[cache_group_name] = create_cache_metrics_group()

        success = local_cache_delete(
            cache=self._local_cache,
            cache_key=cache_key,
            cache_group_name=cache_group_name,
        )

        if success:
            self._cache_metrics[cache_group_name]['local_cache']['delete'] += 1

        # Bail early if we do not have an external cache
        if local_only is False and self.external_cache.cache_client is None:
            log.warning(
                "CacheClient: {0}: DELETE: No CacheClient Available".format(self.cache_type),
                extra={
                    'error': self.external_cache.cache_error
                }
            )

        if self.external_cache.cache_client is None or local_only:
            log.debug(
                "CacheClient: Local: DELETE: Returned",
                extra={
                    'cache_type': self.cache_type,
                    'cache_group_name': cache_group_name,
                    'cache_key': cache_key,
                    'local_only': local_only
                }
            )
            return

        timer_start = datetime.now()
        success, _, err = self.external_cache.delete(cache_key, request_label)

        timer_delta = datetime.now() - timer_start
        if success:
            self._cache_metrics[cache_group_name]['external_cache']['delete'] += 1

        log.debug(
            "CacheClient: {0}: DELETE".format(self.cache_type),
            extra={
                'suceess': success,
                'error': err,
                'response_time_msecs': timer_delta.microseconds,
            }
        )

        return cache_key

    def count(self, cache_group_name='default', filter=None):
        """Local-only cache items count within cache group.
        """
        cache_group = self._local_cache.get(cache_group_name, None)
        if cache_group is None:
            return 0

        if filter is not None:
            if not isinstance(filter, types.LambdaType):
                raise ValueError(error_message="Filter is not a valid lambda expression.")
            return filter(cache_group)

        return len(cache_group)

    def _calculate_metric_totals(self):
        totals = create_cache_metrics_group()

        for _, metrics_group in self._cache_metrics.items():
            for k in metrics_group['local_cache'].keys():
                totals['local_cache'][k] += sum(d[k] for c, d in metrics_group.items() if c == 'local_cache')

        if self.external_cache is None:
            self._cache_metrics['totals'] = totals
            return

        for group_name, metrics_group in self._cache_metrics.items():
            puts = metrics_group['external_cache']['put']
            self._cache_metrics[group_name]['external_cache']['put']['total'] = sum(n for _, n in puts.items())

            external_cache = metrics_group['external_cache']
            for k in external_cache.keys():
                if k == 'put':
                    continue
                totals['external_cache'][k] += sum(d[k] for c, d in metrics_group.items() if c == 'external_cache')

            # Sums by expiration times and gets the totals we calculated above
            for k in external_cache['put'].keys():
                totals['external_cache']['put'][k] = 0
                totals['external_cache']['put'][k] += sum(
                    d['put'][k] for c, d in metrics_group.items() if c == 'external_cache'
                )

        self._cache_metrics['totals'] = totals

    def show_summary(self):
        self._calculate_metric_totals()
        log.info('CacheClient Metrics', extra={'metrics': self._cache_metrics})

    def export_metrics_in_statsd_format(self, required_cache_groups=['totals', 'campaign_sites']):
        '''
        "Flatten" stats in self._cache_metrics, to comply with statsd standard.

        self._cache_metrics is a 'hierarchical' metrics: It maps metrics groups names to
        lower hierarchy nested metrics dictionary.
        In the lowest level, the value is not a dictionary but a literal value.
        ( Look at the example below )
        :return: A 'flattened' metrics, mapping keys, which are statsd format metrics names
        to their values.
        ( Look at the example below )

        For instance, if self._cache_metrics is:
        {'campaign_sites': {'external_cache': {'delete': 0,
                                           'hit': 3,
                                           'miss': 0,
                                           'put': {'total': 0}},
                            'local_cache': {'delete': 0,
                                            'hit': 0,
                                            'miss': 3,
                                            'put': 3}},
         'totals': {'external_cache': {'delete': 0,
                                   'hit': 3,
                                   'miss': 0,
                                   'put': {'total': 0}},
                    'local_cache': {'delete': 0, 'hit': 0, 'miss': 3, 'put': 3}}}


        then the output of this method should be:
        {
            'cache.external.campaign_sites.delete': 0,
            'cache.external.campaign_sites.hit': 3,
            'cache.external.campaign_sites.miss': 0,
            'cache.external.campaign_sites.put.total': 0,
            'cache.local.campaign_sites.delete': 0,
            'cache.local.campaign_sites.hit': 0,
            'cache.local.campaign_sites.miss': 3,
            'cache.local.campaign_sites.put': 3,
            'cache.external.totals.delete': 0,
            'cache.external.totals.hit': 3,
            'cache.external.totals.miss': 0,
            'cache.external.totals.put.total': 0,
            'cache.local.totals.delete': 0,
            'cache.local.totals.hit': 0,
            'cache.local.totals.miss': 3,
            'cache.local.totals.put': 3,
        }
        '''

        cache_type_to_display_name = {
            'external_cache': 'external',
            'local_cache': 'local',
        }
        statsd_metric_2_value_dict = dict()
        for cache_group, cache_type_metrics in self._cache_metrics.items():
            if cache_group not in required_cache_groups:
                continue
            for cache_type, metrics in cache_type_metrics.items():
                for metric_name, metric_value in metrics.items():
                    if type(metric_value) is dict:
                        for metric_sub_name, metric_atomic_value in metric_value.items():
                            metric_full_name = "{}.{}".format(metric_name, metric_sub_name)
                            metric_display_name = "cache.{}.{}.{}".format(
                                cache_type_to_display_name[cache_type],
                                cache_group,
                                metric_full_name,
                            )
                            statsd_metric_2_value_dict[metric_display_name] = metric_atomic_value
                    else:
                        metric_display_name = "cache.{}.{}.{}".format(
                            cache_type_to_display_name[cache_type],
                            cache_group,
                            metric_name,
                        )
                        statsd_metric_2_value_dict[metric_display_name] = metric_value
        return statsd_metric_2_value_dict
