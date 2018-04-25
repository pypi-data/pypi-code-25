# coding: utf-8
import json

from requests.auth import HTTPBasicAuth
from tapioca import (
    TapiocaAdapter, generate_wrapper_from_adapter, JSONAdapterMixin)

from .resource_mapping import RESOURCE_MAPPING


class NessusClientAdapter(JSONAdapterMixin, TapiocaAdapter):
    api_root = None
    resource_mapping = RESOURCE_MAPPING

    def get_api_root(self, api_params):
        return api_params.get('api_root', 'https://localhost:8834')

    def get_request_kwargs(self, api_params, *args, **kwargs):
        params = super(NessusClientAdapter, self).get_request_kwargs(
            api_params, *args, **kwargs)

        access_key = api_params.get('accessKey')
        secret_key = api_params.get('secretKey')

        if access_key and secret_key:
            params['headers'].update({'X-Apikeys': f'accessKey={access_key}; secretKey={secret_key}'})
        else:
            params['auth'] = HTTPBasicAuth(api_params.get('user'), api_params.get('password'))

        return params

    def get_iterator_list(self, response_data):
        return response_data

    def get_iterator_next_request_kwargs(self, iterator_request_kwargs,
                                         response_data, response):
        pass

    def response_to_native(self, response):
        if response.headers._store['content-type'][1] == 'application/octet-stream':
            return response

        elif response.content.strip():
            return response.json()

    def format_data_to_request(self, data):
        if data:
            try:
                return json.dumps(data)
            except:
                return data

Nessus = generate_wrapper_from_adapter(NessusClientAdapter)
