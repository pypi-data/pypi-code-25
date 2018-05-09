# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_restful.decorators import parse_resp_json


class SSOModel(object):

    def __init__(self, app_secret, server_url):
        if not hasattr(settings, 'SSO_APP_ID'):
            raise ImproperlyConfigured('SSO_APP_ID')

        if app_secret is None:
            if not hasattr(settings, 'SSO_APP_SECRET'):
                raise ImproperlyConfigured(
                    'SSO_APP_SECRET')
            app_secret = settings.SSO_APP_SECRET

        if server_url is None:
            if not hasattr(settings, 'SSO_SERVER_URL'):
                raise ImproperlyConfigured('SSO_SERVER_URL')
            server_url = settings.SSO_SERVER_URL

        self.app_id = settings.SSO_APP_ID
        self.app_secret = app_secret
        self.server_url = server_url

    @parse_resp_json
    def get_session(self, sso_code):
        payload = {'app_id': self.app_id, 'app_secret': self.app_secret, 'code': sso_code,
                   'grant_type': 'authorization_code'}
        return requests.get(self.server_url, params=payload)
