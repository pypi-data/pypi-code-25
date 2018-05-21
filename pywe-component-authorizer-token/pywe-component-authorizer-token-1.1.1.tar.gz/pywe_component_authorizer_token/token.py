# -*- coding: utf-8 -*-

import time

from pywe_component_token import component_access_token
from pywe_exception import WeChatException

from .basetoken import BaseComponentAuthorizerToken


class ComponentAuthorizerToken(BaseComponentAuthorizerToken):
    def __init__(self, component_appid=None, component_secret=None, auth_code=None, storage=None, token_fetched_func=None, auth_token_fetched_func=None):
        super(ComponentAuthorizerToken, self).__init__(component_appid=component_appid, component_secret=component_secret, auth_code=auth_code, storage=storage, token_fetched_func=token_fetched_func, auth_token_fetched_func=auth_token_fetched_func)
        # 授权流程技术说明, Refer: https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1&id=open1453779503&token=&lang=zh_CN
        # 4、使用授权码换取公众号或小程序的接口调用凭据和授权信息
        # 该API用于使用授权码换取授权公众号或小程序的授权信息，并换取authorizer_access_token和authorizer_refresh_token。 授权码的获取，需要在用户在第三方平台授权页中完成授权流程后，在回调URI中通过URL参数提供给第三方平台方。请注意，由于现在公众号或小程序可以自定义选择部分权限授权给第三方平台，因此第三方平台开发者需要通过该接口来获取公众号或小程序具体授权了哪些权限，而不是简单地认为自己声明的权限就是公众号或小程序授权的权限。
        # 5、获取（刷新）授权公众号或小程序的接口调用凭据（令牌）
        # 该API用于在授权方令牌（authorizer_access_token）失效时，可用刷新令牌（authorizer_refresh_token）获取新的令牌。请注意，此处token是2小时刷新一次，开发者需要自行进行token的缓存，避免token的获取次数达到每日的限定额度。
        self.WECHAT_FETCH_AUTHORIZER_TOKEN = self.API_DOMAIN + '/cgi-bin/component/api_query_auth?component_access_token={component_access_token}'
        self.WECHAT_REFRESH_AUTHORIZER_TOKEN = self.API_DOMAIN + '/cgi-bin/component/api_authorizer_token?component_access_token={component_access_token}'

    def __about_to_expires(self, expires_at):
        return expires_at and expires_at - int(time.time()) < 60

    def __fetch_authorizer_access_token(self, component_appid=None, component_secret=None, auth_code=None, storage=None, token_fetched_func=None, auth_token_fetched_func=None, with_authorizer_appid=False):
        # Update Params
        self.update_params(component_appid=component_appid, component_secret=component_secret, auth_code=auth_code, storage=storage, token_fetched_func=token_fetched_func, auth_token_fetched_func=auth_token_fetched_func)
        # Component Authorizer Token Request
        token = component_access_token(appid=self.component_appid, secret=self.component_secret, storage=self.storage, token_fetched_func=self.token_fetched_func)
        component_authorizer_access_info = self.post(self.WECHAT_FETCH_AUTHORIZER_TOKEN.format(component_access_token=token), data={
            'component_appid': self.component_appid,
            'authorization_code': self.auth_code,
        }).get('authorization_info', {})
        # Request Error
        if 'expires_in' not in component_authorizer_access_info:
            raise WeChatException(component_authorizer_access_info)
        # Set Authorizer Access Info into Storage
        expires_in = component_authorizer_access_info.get('expires_in')
        component_authorizer_access_info['expires_at'] = int(time.time()) + expires_in
        authorizer_appid = component_authorizer_access_info.get('authorizer_appid', '')
        self.storage.set(self.component_authorizer_access_info_key(authorizer_appid=authorizer_appid), component_authorizer_access_info)
        # If auth_token_fetched_func, Call it with `appid`, `secret`, `access_info`
        if auth_token_fetched_func:
            auth_token_fetched_func(self.component_appid, self.component_secret, authorizer_appid, component_authorizer_access_info)
        # Return Access Token
        if with_authorizer_appid:
            return component_authorizer_access_info.get('authorizer_access_token'), authorizer_appid
        return component_authorizer_access_info.get('authorizer_access_token')

    def __refresh_authorizer_access_token(self, component_appid=None, component_secret=None, authorizer_appid=None, storage=None, token_fetched_func=None, auth_token_fetched_func=None):
        # Update Params
        self.update_params(component_appid=component_appid, component_secret=component_secret, storage=storage, token_fetched_func=token_fetched_func)
        # Component Authorizer Token Refresh Request
        token = component_access_token(appid=self.component_appid, secret=self.component_secret, storage=self.storage, token_fetched_func=self.token_fetched_func)
        component_authorizer_access_info = self.post(self.WECHAT_REFRESH_AUTHORIZER_TOKEN.format(component_access_token=token), data={
            'component_appid': self.component_appid,
            'authorizer_appid': authorizer_appid,
            'authorizer_refresh_token': self.storage.get(self.component_authorizer_access_info_key(authorizer_appid=authorizer_appid), default={}).get('authorizer_refresh_token', ''),
        })
        # Request Error
        if 'expires_in' not in component_authorizer_access_info:
            raise WeChatException(component_authorizer_access_info)
        # Set Authorizer Access Info into Storage
        expires_in = component_authorizer_access_info.get('expires_in')
        component_authorizer_access_info['expires_at'] = int(time.time()) + expires_in
        self.storage.set(self.component_authorizer_access_info_key(authorizer_appid=authorizer_appid), component_authorizer_access_info)
        # If token_fetched_func, Call it with `appid`, `secret`, `access_info`
        if auth_token_fetched_func:
            auth_token_fetched_func(self.component_appid, self.component_secret, authorizer_appid, component_authorizer_access_info)
        # Return Access Token
        return component_authorizer_access_info.get('authorizer_access_token')

    def get_authorizer_access_token(self, component_appid=None, component_secret=None, authorizer_appid=None, storage=None, token_fetched_func=None, auth_token_fetched_func=None):
        # Update Params
        self.update_params(component_appid=component_appid, component_secret=component_secret, storage=storage, token_fetched_func=token_fetched_func, auth_token_fetched_func=auth_token_fetched_func)
        # Fetch component_authorizer_access_info
        component_authorizer_access_info = self.storage.get(self.component_authorizer_access_info_key(authorizer_appid=authorizer_appid))
        if component_authorizer_access_info:
            authorizer_access_token = component_authorizer_access_info.get('authorizer_access_token')
            if authorizer_access_token and not self.__about_to_expires(component_authorizer_access_info.get('expires_at')):
                return authorizer_access_token
        return self.__refresh_authorizer_access_token(self.component_appid, self.component_secret, authorizer_appid, self.storage, token_fetched_func=self.token_fetched_func, auth_token_fetched_func=self.auth_token_fetched_func)

    def initial_authorizer_access_token(self, component_appid=None, component_secret=None, auth_code=None, storage=None, token_fetched_func=None, auth_token_fetched_func=None, with_authorizer_appid=False):
        return self.__fetch_authorizer_access_token(component_appid, component_secret, auth_code, storage, token_fetched_func=token_fetched_func, auth_token_fetched_func=auth_token_fetched_func, with_authorizer_appid=with_authorizer_appid)

    def refresh_authorizer_access_token(self, component_appid=None, component_secret=None, authorizer_appid=None, storage=None, token_fetched_func=None, auth_token_fetched_func=None):
        return self.__refresh_authorizer_access_token(component_appid, component_secret, authorizer_appid, storage, token_fetched_func=token_fetched_func, auth_token_fetched_func=auth_token_fetched_func)

    def final_authorizer_access_token(self, cls=None, component_appid=None, component_secret=None, authorizer_access_token=None, authorizer_appid=None, storage=None, token_fetched_func=None, auth_token_fetched_func=None):
        return authorizer_access_token or self.get_authorizer_access_token(component_appid or cls.component_appid, component_secret or cls.component_secret, authorizer_appid, storage=storage or cls.storage, token_fetched_func=token_fetched_func or cls.token_fetched_func, auth_token_fetched_func=auth_token_fetched_func)


token = ComponentAuthorizerToken()
authorizer_access_token = token.get_authorizer_access_token
initial_authorizer_access_token = token.initial_authorizer_access_token
refresh_authorizer_access_token = token.refresh_authorizer_access_token
final_authorizer_access_token = token.final_authorizer_access_token
