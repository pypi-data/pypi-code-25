# -*- coding: utf-8 -*-

import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_restful import RestfulApiError, DoesNotExistError, parse_resp_json, parse_resp_status
from django_restful.utils import parse_json, build_url


class SessionModel(object):

    def __init__(self, access_token_secret=None, base_url=None):
        if access_token_secret is None:
            if hasattr(settings, 'SAE_API_ACCESS_TOKEN_SECRET'):
                raise ImproperlyConfigured(
                    'SAE_API_ACCESS_TOKEN_SECRET')
            access_token_secret = settings.ACCESS_TOKEN_SECRET

        if base_url is None:
            if hasattr(settings, 'SAE_API_BASE_URL'):
                raise ImproperlyConfigured('SAE_API_BASE_URL')
            base_url = build_url(settings.SAE_API_BASE_URL, 'session')

        self.access_token_secret = access_token_secret
        self.base_url = base_url

    @parse_resp_json
    def get_one(self, session_key):
        url = build_url(self.base_url, session_key)
        return requests.get(url)

    @parse_resp_json
    def get_all(self):
        return requests.get(self.base_url)

    @parse_resp_status
    def add(self, entity):
        resp = requests.post(self.base_url, data=entity)
        return resp

    @parse_resp_status
    def modify(self, entity):
        url = build_url(this.base_url, entity.get('session_key'))
        resp = requests.put(url, data=entity)
        return resp

    @parse_resp_status
    def exist_modify(self, entity):
        url = build_url(this.base_url, 'exists_modify')
        resp = requests.post(url, data=entity)
        return resp

    @parse_resp_status
    def delete(self, session_key):
        url = build_url(this.base_url, session_key)
        resp = requests.delete(url)
        return resp

    @parse_resp_status
    def clear_expired(self):
        ulr = build_url(self.base_url, 'clear_expired')
        resp = requests.post(url, data=entity)
        return resp

    def exists(self, session_key):
        try:
            data = self.get_one(session_key)
        except DoesNotExistError:
            return False
        return True
