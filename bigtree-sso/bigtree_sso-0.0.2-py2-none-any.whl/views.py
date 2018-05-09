# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.views.generic import View
from django.http import Http404, HttpResponsePermanentRedirect, HttpResponseRedirect

from django_restful import DoesNotExistError

from bigtree_sso.encryp import HexAES

from bigtree_api.models.microapp_token import MicroAppTokenModel

logger = logging.getLogger('bigtree_sso')

APP_SECRET = settings.SSO_APP_SECRET
APP_ID = settings.SSO_APP_ID


def _aes_decrypt(session_key):
    """session_key解密"""

    aes = HexAES(APP_SECRET)
    return aes.decrypt(session_key)


def _redirect(redirect_uri, session_id):
    """重定向并写入cookie."""

    response = HttpResponseRedirect(redirect_uri)
    session_id = _aes_decrypt(session_id)
    response.set_cookie(settings.SESSION_COOKIE_NAME, session_id, max_age=None, expires=None,
                        domain=settings.SESSION_COOKIE_DOMAIN,
                        path=settings.SESSION_COOKIE_PATH,
                        secure=settings.SESSION_COOKIE_SECURE or None,
                        httponly=settings.SESSION_COOKIE_HTTPONLY or None)
    return response


class SessionSSOView(View):
    """将返回的session_id写入到cookie并重定向到redirect_uri。
    """

    def get(self, request, *args, **kwargs):
        query = request.GET.copy()
        redirect_uri = query.get('redirect_uri', None)
        session_id = query.get('session_id', None)

        if redirect_uri and session_id:
            return _redirect(redirect_uri, session_id)
        raise Http404


class DebugCodeSSOView(View):
    """代码调试阶段使用，通过临时票据code获取session_id,并将session_id写入到cookie和重定向到redirect_uri。
    """

    def get(self, request, *args, **kwargs):
        if not settings.DEBUG:
            raise Http404

        logger.warning('DebugCodeSSOView仅能在代码调试阶段使用,正式环境请切换到CodeSSOView。')

        query = request.GET.copy()
        redirect_uri = query.get('redirect_uri', None)
        state = query.get('state', None)

        code = settings.SSO_TEST_CODE

        if redirect_uri and code:
            try:
                service = MicroAppTokenModel()
                s = service.access_token(APP_ID, code)
                session_id = s.get('session_id', '')
                return _redirect(redirect_uri, session_id)
            except DoesNotExistError:
                raise Http404
        raise Http404


class CodeSSOView(View):
    """通过临时票据code获取session_id,并将session_id写入到cookie和重定向到redirect_uri。
    """

    def get(self, request, *args, **kwargs):
        query = request.GET.copy()
        redirect_uri = query.get('redirect_uri', None)
        code = query.get('code', None)
        state = query.get('state', None)

        if redirect_uri and code:
            try:
                service = MicroAppTokenModel()
                s = service.access_token(APP_ID, code)
                session_id = s.get('session_id', '')
                return _redirect(redirect_uri, session_id)
            except DoesNotExistError:
                raise Http404
        raise Http404
