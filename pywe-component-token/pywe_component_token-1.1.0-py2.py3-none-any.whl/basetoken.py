# -*- coding: utf-8 -*-

import time

from pywe_base import BaseWechat
from pywe_storage import MemoryStorage


class BaseComponentToken(BaseWechat):
    def __init__(self, appid=None, secret=None, token=None, storage=None, token_fetched_func=None):
        super(BaseComponentToken, self).__init__()
        self.appid = appid
        self.secret = secret
        self.token = token
        self.storage = storage or MemoryStorage()
        self.token_fetched_func = token_fetched_func

        if self.token:
            expires_in = 7200
            component_access_info = {
                'component_access_token': self.token,
                'expires_in': expires_in,
                'expires_at': int(time.time()) + expires_in,
            }
            self.storage.set(self.component_access_info_key, component_access_info, expires_in)

    @property
    def component_access_info_key(self):
        return '{0}:component:access:info'.format(self.appid)

    def update_params(self, appid=None, secret=None, token=None, storage=None, token_fetched_func=None):
        self.appid = appid or self.appid
        self.secret = secret or self.secret
        self.token = token or self.token
        self.storage = storage or self.storage
        self.token_fetched_func = token_fetched_func or self.token_fetched_func
