# -*- coding: utf-8 -*-
import pkg_resources
import platform

API_YOUTU_END_POINT = 'http://api.youtu.qq.com/'
API_TENCENTYUN_END_POINT = 'https://youtu.api.qcloud.com/'
API_YOUTU_VIP_END_POINT = 'https://vip-api.youtu.qq.com/'

APPID = '10114485'
SECRET_ID = 'AKIDYtynLcYPu98rJVP6VdV7TYNyJOCkP6wW'
SECRET_KEY = 'SeZEcniMjqgIejXUDhvwhCRRAdqnUu4x'
USER_ID = '382771946'

_config = {
    'end_point':API_YOUTU_END_POINT,
    'appid':APPID,
    'secret_id':SECRET_ID,
    'secret_key':SECRET_KEY,
    'userid':USER_ID,
}

def get_app_info():
    return _config

def set_app_info(appid=None, secret_id=None, secret_key=None, userid=None, end_point=None):
    if appid:
        _config['appid'] = appid
    if secret_id:
        _config['secret_id'] = secret_id
    if secret_key:
        _config['secret_key'] = secret_key
    if userid:
        _config['userid'] = userid
    if end_point:
        _config['end_point'] = end_point
