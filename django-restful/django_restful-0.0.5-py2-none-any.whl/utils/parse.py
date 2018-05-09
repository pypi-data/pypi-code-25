# -*- coding: utf-8 -*-

import json

from django_restful import RestfulApiError, DoesNotExistError


def _check_server_error(json_data):
    """如果返回的数据不是json则有可能是api的服务器错误返回的html.
    """
    if "Exceeded connection limit for user" in json_data:
        raise RestfulApiError(
            {'message': "Exceeded connection limit for user"})
    if "Error 401 Unauthorized" in json_data:
        raise RestfulApiError({'message': "Unauthorized"})
    raise RestfulApiError({'Unknown error: {0}'.format(json_data)})


def _check_api_error(data):
    # 首先检查API是否返回错误，而不是尝试捕捉异常
    if 'error' in data:
        if 'DoesNotExist' in data:
            raise DoesNotExistError(data['error'])
        raise RestfulApiError(data['error'])


def parse_json(json_data):
    """尝试解析从api返回的json,并在出现错误时返回一个空的字典.
    """
    try:
        data = json.loads(json_data)
    except ValueError:
        # 如果返回的数据不是json则有可能是api返回的html错误信息信息，则抛出不同的异常.
        _check_server_error(json_data)

    # 检查是否是接口返回的错误提示数据
    _check_api_error(data)
    return data


def parse_resp(resp, decode='utf-8'):
    """尝试解析从api返回的response,该response的content需为json，并在出现错误时返回一个空的字典.
    """
    json_data = resp.content.decode('utf-8')
    return parse_json(json_data)


def parse_status(resp):
    """解析response的status_code，返回true, false.
    """
    if resp.status_code not in [204, 201, 202]:
        return parse_resp(resp)
    return True
