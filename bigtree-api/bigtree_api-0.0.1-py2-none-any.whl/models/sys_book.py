# -*- coding: utf-8 -*-

import requests

from django_restful import parse_resp_json
from django_restful.utils.url import build_url

from .base import BaseModel


class SysBookModel(BaseModel):
    model_url = 'sys_book'

    @parse_resp_json
    def get_all(self):
        resp = requests.get(self.service_url, headers=self.token_header)
        return resp

    @parse_resp_json
    def get_list_class_code(self, class_code):
        url = build_url(self.service_url, 'class_code')

        payload = {'class_code': class_code}
        resp = requests.get(url, params=payload, headers=self.token_header)
        return resp
