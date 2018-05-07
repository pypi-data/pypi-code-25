# -*- coding: utf-8 -*-

import requests
from django_restful import parse_resp_json

from .base import BaseModel


class SysConfigModel(BaseModel):
    model_url = 'sys_config'

    @parse_resp_json
    def get_all(self):
        resp = requests.get(self.service_url, headers=self.token_header)
        return resp
