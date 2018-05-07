# -*- coding: utf-8 -*-

import requests
from django_restful import parse_resp_status

from .base import BaseModel


class AuthUserLogModel(BaseModel):
    model_url = 'auth_user_log'

    @parse_resp_status
    def add(self, entity):
        resp = requests.post(self.service_url, data=entity,
                             headers=self.token_header)
        return resp
