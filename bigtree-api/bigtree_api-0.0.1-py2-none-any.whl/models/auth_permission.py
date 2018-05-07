# -*- coding: utf-8 -*-

import requests
from django_restful import parse_resp_json

from .base import BaseModel


class AuthPermissionModel(BaseModel):
    model_url = 'auth_permission'

    @parse_resp_json
    def get_all(self):
        resp = requests.get(self.service_url, headers=self.token_header)
        return resp
