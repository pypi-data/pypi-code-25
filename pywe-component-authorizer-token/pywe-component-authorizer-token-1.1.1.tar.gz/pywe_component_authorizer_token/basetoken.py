# -*- coding: utf-8 -*-

import time

from pywe_base import BaseWechat
from pywe_exception import WeChatException
from pywe_storage import MemoryStorage, ShoveStorage


class BaseComponentAuthorizerToken(BaseWechat):
    def __init__(self, component_appid=None, component_secret=None, auth_code=None, auth_access_token=None, auth_refresh_token=None, storage=None, token_fetched_func=None, auth_token_fetched_func=None):
        super(BaseComponentAuthorizerToken, self).__init__()
        self.component_appid = component_appid
        self.component_secret = component_secret
        self.auth_code = auth_code
        self.auth_access_token = auth_access_token
        self.auth_refresh_token = auth_refresh_token
        self.storage = storage
        self.token_fetched_func = token_fetched_func
        self.auth_token_fetched_func = auth_token_fetched_func

    def component_authorizer_access_info_key(self, authorizer_appid=None):
        return '{0}:{1}:component:authorizer:access:info'.format(self.component_appid, authorizer_appid)

    def update_params(self, component_appid=None, component_secret=None, auth_code=None, auth_access_token=None, auth_refresh_token=None, storage=None, token_fetched_func=None, auth_token_fetched_func=None):
        self.storage = storage or self.storage

        if self.storage is None or isinstance(self.storage, (MemoryStorage, ShoveStorage)):
            raise WeChatException('Can not use memory storage, Use RedisStorage or MemcachedStorage instead.')

        self.component_appid = component_appid or self.component_appid
        self.component_secret = component_secret or self.component_secret
        self.auth_code = auth_code or self.auth_code
        self.auth_access_token = auth_access_token or self.auth_access_token
        self.auth_refresh_token = auth_refresh_token or self.auth_refresh_token
        self.token_fetched_func = token_fetched_func or self.token_fetched_func
        self.auth_token_fetched_func = auth_token_fetched_func or self.auth_token_fetched_func
