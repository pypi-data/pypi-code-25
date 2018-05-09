# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_restful.utils import build_url


class BaseModel(object):

    def __init__(self, base_url, access_token_secret=None):
        if access_token_secret is None:
            if not hasattr(settings, 'SAE_ACCESS_TOKEN_SECRET'):
                raise ImproperlyConfigured(
                    'SAE_ACCESS_TOKEN_SECRET')
            access_token_secret = settings.SAE_ACCESS_TOKEN_SECRET

        self.base_url = base_url
        self.access_token_secret = access_token_secret

        self.token_header = {
            'SAE_ACCESS_TOKEN_SECRET': access_token_secret}
