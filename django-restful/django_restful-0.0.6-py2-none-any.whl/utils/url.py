# -*- coding: utf-8 -*-

import six

from urllib import urlencode

from urlparse import urlparse, urlunparse
from django_restful import RestfulApiError


def _encode_parameters(parameters):
    """Return a string in key=value&key=value form.

    Values of None are not included in the output string.

    Args:
      parameters (dict): dictionary of query parameters to be converted into a
      string for encoding and sending to Twitter.

    Returns:
      A URL-encoded string in "key=value&key=value" form
    """
    if parameters is None:
        return None
    if not isinstance(parameters, dict):
        raise RestfulApiError("`parameters` must be a dict.")
    else:
        params = dict()
        for k, v in parameters.items():
            if v is not None:
                if getattr(v, 'encode', None):
                    v = v.encode('utf8')
                params.update({k: v})
        return urlencode(params)


def build_url(url, path_elements=None, extra_params=None):
    # 将网址分解成组成部分
    (scheme, netloc, path, params, query, fragment) = urlparse(url)

    if isinstance(path_elements, six.string_types):
        path_elements = (path_elements,)

    # 将其他路径元素添加到路径中
    if path_elements:
        if not path.endswith('/'):
            path += '/'

        # 过滤出值为None的路径元素
        filtered_elements = [i for i in path_elements if i]
        path += '/'.join(filtered_elements)

    if not path.endswith('/'):
        path += '/'

    # 将任何其他查询参数添加到查询字符串
    if extra_params and len(extra_params) > 0:
        extra_query = _encode_parameters(extra_params)
        # 将其添加到现有的查询中
        if query:
            query += '&' + extra_query
        else:
            query = extra_query

    # 返回重建的网址
    return urlunparse((scheme, netloc, path, params, query, fragment))
