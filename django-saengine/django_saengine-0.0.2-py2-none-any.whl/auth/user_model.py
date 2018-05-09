# -*- coding: utf-8 -*-

import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_restful import RestfulApiError, parse_resp_json
from django_restful.utils import build_url


class UserModel(object):

    def __init__(self, access_token_secret=None, base_url=None):
        if access_token_secret is None:
            if hasattr(settings, 'SAE_API_ACCESS_TOKEN_SECRET'):
                raise ImproperlyConfigured(
                    'SAE_API_ACCESS_TOKEN_SECRET')
            access_token_secret = settings.ACCESS_TOKEN_SECRET

        if base_url is None:
            if hasattr(settings, 'SAE_API_BASE_URL'):
                raise ImproperlyConfigured('SAE_API_BASE_URL')
            base_url = build_url(settings.SAE_API_BASE_URL, 'user')

        self.access_token_secret = access_token_secret
        self.base_url = base_url

    @parse_resp_json
    def authenticate(self, login_name, login_pwd):
        url = build_url(self.base_url, 'authenticate')
        data = {'login_name': login_name, 'login_pwd': login_pwd}
        return requests.post(url, data=data)

    @parse_resp_json
    def get_user(self, user_id):
        url = build_url(self.base_url, user_id)
        return requests.get(url)
