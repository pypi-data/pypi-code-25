# Copyright 2017 Shortest Track Company. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.

"""Implements HTTP client helper functionality."""
import datetime

import requests

from st_library import exceptions
from st_library.utils.helpers.store import Store
from st_library.utils.shared_toolkit.api_client import BaseApiClient, SecAccessTokenMixin

METHOD_GET = 'get'
METHOD_POST = 'post'
METHOD_DELETE = 'delete'


class DisabledLogger(object):
    def __getattr__(self, item):
        def _mock(*args, **kwargs):
            pass

        return _mock


_disabled_logger = DisabledLogger()


class _SharedApiClientAdapter(BaseApiClient, SecAccessTokenMixin):
    DELETE = 'delete'

    def _get_cache_sec_access_token_expiration(self, configuration_id):
        return Store.token_data.get('expiration')

    def _get_auth_string(self):
        return 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjNDkzZmI5MS02YWE4LTRiODItYjA2Ni0wZTkxYzQ4MjZkOTciLCJhdWQiOlsid2ViX2FwcCJdLCJjb21wYW55SWQiOiJzaG9ydGVzdHRyYWNrX3Jvb3RfYWRtaW5fY29tcGFueSIsInNjb3BlIjpbIm9wZW5pZCJdLCJpc3MiOiJzaG9ydGVzdHRyYWNrLXVhYSIsImV4cCI6MTUyMzcwNjU0OCwiaWF0IjoxNTIzNzA2MjQ4LCJhdXRob3JpdGllcyI6WyJST0xFX1JPT1QiXSwianRpIjoiNzlhOTEyNTktODc2Mi00OTE0LTgxOTgtMTVhOTk0M2ExMzQwIiwiZW1haWwiOiJyb290QGxvY2FsaG9zdCIsImNsaWVudF9pZCI6IndlYl9hcHAifQ.fBOQBe_y7gJO_Rm45o1HlnObkpoEPz0o22A0crlH1CAnYgSmGYog4yU4OuWveVQqNK92Lmsl2M2M7f_Hyqbret8b56PwEiLCOVlIqGPrtwXrfQJfNUoYGwELEpWBD4ERv2Kc8OHivRJp92Qvb9eUmkQ01S31dVj5OU0tbJRSZOk8CiOkmrM3oyIfSqp63dIBQWDmjnlMgrJ7nXsUH_yK5UdzmcPJgdGIk3QxaLbjZDlaewB2Ghc-sdCyOXKcxjK1GinIdAW5d6ZJAp4RcDDnM1Tg1h-TLoxPTk2u09zj7OS67luyaS_0xPMVI0TaF74FKf7TVOPqV0Jv8WxrVVb90Q'
        # return ''

    def get_sec_refresh_token(self, configuration_id):
        return Store.token

    def _set_cache_public_key(self, public_key):
        Store.token_data['public_key'] = public_key

    @property
    def _basic_auth_tuple(self):
        return ('script', 'noMatter',)

    def _raise_performing_request_error(self, *args, **kwargs):
        raise exceptions.ServiceRequestError(*args, **kwargs)

    def _set_cache_sec_access_token(self, configuration_id, access_token):
        Store.token_data['access_token'] = access_token

    def _raise_http_error(self, *args, **kwargs):
        raise exceptions.ServiceRequestError(*args, **kwargs)

    def _get_cache_public_key(self):
        return Store.token_data.get('public_key')

    def _get_cache_sec_access_token(self, configuration_id):
        return Store.token_data.get('access_token')

    def _set_cache_sec_access_token_expiration(self, configuration_id, expiration):
        Store.token_data['expiration'] = expiration

    def _get_logger(self):
        return _disabled_logger

    def request(self, *args, **kwargs):
        if kwargs.get('extra_headers') is None:
            kwargs['extra_headers'] = {}
        kwargs['extra_headers']['User-Agent'] = 'st-dataprovider/1.0'
        return super(_SharedApiClientAdapter, self).request(*args, **kwargs)


_adapter = _SharedApiClientAdapter()


def get(url, params=None, data=None, json=None, extra_headers=None, raw_response=False, stats=None):
    return _adapter.request(_adapter.GET, '', params=params, data=data, json=json, base=url,
                            extra_headers=extra_headers, sec_id_for_special_token=Store.config_id,
                            raw_content=raw_response)


def post(url, params=None, data=None, json=None, extra_headers=None, raw_response=False, stats=None):
    if data is None:
        raise exceptions.InternalError('Cannot perform POST request without data')

    return _adapter.request(_adapter.POST, '', params=params, data=data, json=json, base=url,
                            extra_headers=extra_headers, sec_id_for_special_token=Store.config_id,
                            raw_content=raw_response)


def delete(url, params=None, data=None, json=None, extra_headers=None, raw_response=False, stats=None):
    return _adapter.request(_adapter.DELETE, '', params=params, data=data, json=json, base=url,
                            extra_headers=extra_headers, sec_id_for_special_token=Store.config_id,
                            raw_content=raw_response)
