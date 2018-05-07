# -*- coding: utf-8 -*-

import functools
import six

from .utils.parse import parse_resp, parse_status


def view_http_method(names=None):
    """给view添加http method 约束，默认在不为get.
    """
    names = names or ['get']

    if isinstance(names, six.string_types):
        names = [names]

    names = [m.lower() for m in names]

    def _api_view(fn):
        @functools.wraps(fn)
        def __api_view(*args, **kwargs):
            return fn(*args, **kwargs)

        setattr(__api_view, 'http_method_names', names)
        return __api_view

    return _api_view


def parse_resp_json(fn):
    """尝试解析response的content为json的响应内容.
    """
    @functools.wraps(fn)
    def _parse_resp_json(*args, **kwargs):
        resp = fn(*args, **kwargs)
        return parse_resp(resp)
    return _parse_resp_json


def parse_resp_status(fn):
    """尝试解析response返回的状态.
    """
    @functools.wraps(fn)
    def _parse_resp_status(*args, **kwargs):
        resp = fn(*args, **kwargs)
        parse_status(resp)
    return _parse_resp_status
