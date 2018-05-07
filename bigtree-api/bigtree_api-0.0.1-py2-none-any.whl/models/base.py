# -*- coding: utf-8 -*-

import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_restful.utils.url import build_url


class BaseModel(object):

    def __init__(self, base_url=None, access_token_secret=None):
        if access_token_secret is None:
            if not hasattr(settings, 'BIGTREE_API_ACCESS_TOKEN_SECRET'):
                raise ImproperlyConfigured(
                    'BIGTREE_API_ACCESS_TOKEN_SECRET')
            access_token_secret = settings.BIGTREE_API_ACCESS_TOKEN_SECRET

        if base_url is None:
            if not hasattr(settings, 'BIGTREE_API_BASE_URI'):
                raise ImproperlyConfigured('BIGTREE_API_BASE_URI')
            base_url = settings.BIGTREE_API_BASE_URI

        self.base_url = base_url
        self.service_url = build_url(self.base_url, self.model_url)

        self.access_token_secret = access_token_secret
        self.token_header = {
            'ACCESS_TOKEN_SECRET': access_token_secret}
