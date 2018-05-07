# -*- coding: utf-8 -*-

import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_restful import parse_resp_json


class BaseModel(object):

    def __init__(self, base_url, access_token_secret=None):
        if access_token_secret is None:
            if not hasattr(settings, 'SYS_CONFIG_ACCESS_TOKEN_SECRET'):
                raise ImproperlyConfigured(
                    'SYS_CONFIG_ACCESS_TOKEN_SECRET')
            access_token_secret = settings.SYS_CONFIG_ACCESS_TOKEN_SECRET

        self.base_url = base_url
        self.access_token_secret = access_token_secret

        self.token_header = {
            'SYS_CONFIG_ACCESS_TOKEN_SECRET': access_token_secret}


class SysConfigModel(BaseModel):

    def __init__(self):
        if not hasattr(settings, 'SYS_CONFIG_BACKEND_SERVICE_URL'):
            raise ImproperlyConfigured('SYS_CONFIG_BACKEND_SERVICE_URL')

        base_url = settings.SYS_CONFIG_BACKEND_SERVICE_URL
        super(SysConfigModel, self).__init__(base_url)

    @parse_resp_json
    def get_all(self):
        resp = requests.get(self.base_url, headers=self.token_header)
        return resp
