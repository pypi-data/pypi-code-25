# coding=utf-8

import requests
import json
import sys
from exception.exceptions import ServerException, ClientException

url = 'http://cmdb.speiyou.cn/api'

def doRequest(action_name, data):
    try:
        request_obj = requests.post('{0}/{1}'.format(url, action_name),
                                    data = data)
    except Exception, e:
        raise ClientException('doRequest', e)
    if not request_obj.ok:
        raise ServerException(
            request_obj.status_code,
            request_obj.content
        )
    try:
        request_data = request_obj.json()
    except Exception, e:
        raise ClientException('Json decoding', e)
    return request_data