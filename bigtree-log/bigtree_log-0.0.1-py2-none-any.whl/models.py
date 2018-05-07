# -*- coding: utf-8 -*-

import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_restful import parse_resp_status


class BaseModel(object):

    def __init__(self, base_url, access_token_secret=None):
        if access_token_secret is None:
            if not hasattr(settings, 'LOG_ACCESS_TOKEN_SECRET'):
                raise ImproperlyConfigured(
                    'LOG_ACCESS_TOKEN_SECRET')
            access_token_secret = settings.LOG_ACCESS_TOKEN_SECRET

        self.base_url = base_url
        self.access_token_secret = access_token_secret

        self.token_header = {
            'LOG_ACCESS_TOKEN_SECRET': access_token_secret}


class UserLogModel(BaseModel):

    def __init__(self):
        if not hasattr(settings, 'USER_LOG_BACKEND_SERVICE_URL'):
            raise ImproperlyConfigured('USER_LOG_BACKEND_SERVICE_URL')

        base_url = settings.USER_LOG_BACKEND_SERVICE_URL
        super(UserLogModel, self).__init__(base_url)

    @parse_resp_status
    def add(self, entity):
        resp = requests.post(self.base_url, data=entity,
                             headers=self.token_header)
        return resp
