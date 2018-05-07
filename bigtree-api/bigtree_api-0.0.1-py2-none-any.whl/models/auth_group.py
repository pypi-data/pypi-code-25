# -*- coding: utf-8 -*-

import requests

from django_restful import parse_resp_json
from django_restful.utils.url import build_url

from .base import BaseModel


class AuthGroupModel(BaseModel):
    model_url = 'auth_group'

    @parse_resp_json
    def get_all(self):
        resp = requests.get(self.service_url, headers=self.token_header)
        return resp

    @parse_resp_json
    def get_one(self, group_id):
        url = build_url(self.service_url, group_id)
        resp = requests.get(url, headers=self.token_header)
        return resp
