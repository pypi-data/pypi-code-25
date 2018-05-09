# -*- coding: utf-8 -*-

import requests

from django.conf import settings

from django_restful import RestfulApiError, parse_resp_json
from django_restful.utils import build_url

from .base import BaseModel
from django_restful.decorators import parse_resp_status


class UserModel(BaseModel):

    def __init__(self):
        base_url = settings.SAE_AUTHENTICATE_SERVICE_URL
        super(UserModel, self).__init__(base_url)

    def get_user(self, user_id):
        return self.get_one(user_id)

    @parse_resp_json
    def get_one(self, user_id):
        url = build_url(self.base_url, user_id)
        return requests.get(url, headers=self.token_header)

    @parse_resp_json
    def get_all(self):
        return requests.get(self.base_url, headers=self.token_header)

    @parse_resp_json
    def authenticate(self, login_name, login_pwd):
        url = build_url(self.base_url, 'authenticate')
        data = {'login_name': login_name, 'login_pwd': login_pwd}
        return requests.post(url, data=data, headers=self.token_header)

    @parse_resp_status
    def modify_pwd(self, user_id, old_pwd, new_pwd):
        url = build_url(self.base_url, [user_id, 'modify_pwd'])
        data = {'old_pwd': old_pwd, 'new_pwd': new_pwd}
        return requests.post(url, data=data, headers=self.token_header)
