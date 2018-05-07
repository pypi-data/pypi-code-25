# -*- coding: utf-8 -*-

import requests
from django_restful.decorators import parse_resp_json
from django_restful.utils.url import build_url

from .base import BaseModel


class MicroAppTokenModel(BaseModel):

    model_url = 'microapp_token'

    @parse_resp_json
    def access_token(self, app_id, token_code):
        """ 通过临时会话票据获取session.

        @param app_id: 微应用的code.
        @param token_code: 临时会话凭据.

        @return: 返回字典{'session_id': '', 'expire_date': ''}，其中session_id需要解密后使用。
        """
        payload = {'appid': app_id, 'token_code': token_code,
                   'grant_type': 'authorization_code'}

        url = build_url(self.service_url, 'access_token')
        return requests.get(url, params=payload, headers=self.token_header)
