# -*- coding: utf-8 -*-

import requests

from django.conf import settings

from django_restful import RestfulApiError, DoesNotExistError, parse_resp_json, parse_resp_status
from django_restful.utils import parse_json, build_url

from .base import BaseModel


class SessionModel(BaseModel):

    def __init__(self):
        base_url = settings.SAE_SESSION_SERVICE_URL
        super(SessionModel, self).__init__(base_url)

    @parse_resp_json
    def get_one(self, session_key):
        """获取一条数据"""
        url = build_url(self.base_url, session_key)
        return requests.get(url, headers=self.token_header)

    @parse_resp_json
    def get_all(self):
        """获取所有数据"""
        return requests.get(self.base_url, headers=self.token_header)

    @parse_resp_status
    def add(self, entity):
        """新增一条数据"""
        resp = requests.post(self.base_url, data=entity,
                             headers=self.token_header)
        return resp

    @parse_resp_status
    def modify(self, entity):
        """修改数据"""
        url = build_url(self.base_url, entity.get('session_key'))
        resp = requests.put(url, data=entity, headers=self.token_header)
        return resp

    @parse_resp_status
    def delete(self, session_key):
        """删除一条数据"""
        url = build_url(self.base_url, session_key)
        resp = requests.delete(url, headers=self.token_header)
        return resp

    @parse_resp_json
    def get_page_query(self, limit, offset, sort=None, order=None):
        """获取分页记录"""
        url = build_url(self.base_url, 'pager')
        payload = {'limit': limit, 'offset': offset}

        if sort:
            payload['sort'] = sort
        if order:
            payload['order'] = order
        return requests.get(url, params=payload, headers=self.token_header)

    @parse_resp_status
    def exist_modify(self, entity):
        """数据存在修改，不存在新增"""
        url = build_url(self.base_url, 'exists_modify')
        resp = requests.post(url, data=entity, headers=self.token_header)
        return resp

    @parse_resp_status
    def tran_delete(self, pks):
        """删除多条记录
        @param pks: 主键列表
        """
        url = build_url(self.base_url, 'tran_delete')
        resp = requests.post(
            url, data={'pks': '|'.join(pks)}, headers=self.token_header)
        return resp

    @parse_resp_status
    def clear(self):
        """清空数据，删除所有数据"""
        url = build_url(self.base_url, 'clear')
        resp = requests.post(url, headers=self.token_header)
        return resp

    @parse_resp_status
    def clear_expired(self):
        """清除过期数据"""
        url = build_url(self.base_url, 'clear_expired')
        resp = requests.post(url, headers=self.token_header)
        return resp

    def exists(self, session_key):
        """是否存在
        @return: true or false
        """
        try:
            data = self.get_one(session_key)
        except DoesNotExistError:
            return False
        return True
