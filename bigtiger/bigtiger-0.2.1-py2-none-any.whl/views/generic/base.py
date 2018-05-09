# -*- coding: utf-8 -*-

'''
Created on 2017-6-22
@author: linkeddt.com
'''

import functools

from django.conf import settings
from django.http import Http404
from django.views.generic.base import ContextMixin
from django.template.response import TemplateResponse

from bigtiger.contrib.log.signals import user_log_success, user_log_error
from bigtiger.core.exceptions import PermissionError


def permission(fn):
    """权限控制"""

    @functools.wraps(fn)
    def _permission(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
            return result
        except PermissionError:
            request = args[1]
            redirect_url = '/'
            if hasattr(settings, 'LOGOUT_URL'):
                redirect_url = settings.LOGOUT_URL
            return TemplateResponse(request, 'admin/redirect_template.htm', {'redirect_url': redirect_url})
        except Exception as e:
            print e
    return _permission


class SysConfContextMixin(ContextMixin):
    """ 读取配置文件中的系统全局配置到context中
    """

    def get_context_data(self, **kwargs):
        sys_conf = {}
        if hasattr(settings, 'SYS_CONFIG'):
            sys_conf = settings.SYS_CONFIG
        if hasattr(settings, 'ONLINE'):
            sys_conf.update(settings.ONLINE.configs)

        kwargs['sysconf'] = sys_conf
        return super(SysConfContextMixin, self).get_context_data(**kwargs)


class PkContextMixin(object):
    pk_url_kwarg = 'pk'
    pk_split_kwarg = ','

    def __init__(self):
        self.__key = None

    def get_key(self):
        if self.__key is None:
            self.__key = self.kwargs.get(self.pk_url_kwarg, '')
        return self.__key

    def get_pks(self):
        key = self.get_key()
        return key.split(self.pk_split_kwarg)


class PermissionMixin(object):
    ref_url_kwarg = 'ref'

    def get_url_permission(self, url=None):
        if url is None:
            url = self.request.GET.get(
                self.ref_url_kwarg, None) or self.request.path

        ps = self.get_session_permissions()
        if ps is None:
            raise PermissionError()

        ps = [item for item in ps if item['menu_url'] == url]
        return None if len(ps) == 0 else ps[0]

    def get_session_permissions(self):
        return self.request.session.get(settings.PERMISSIONS_SESSION_KEY, None)


class MimeTypeContextMixin(object):
    mime_type_kwarg = 'MIME_TYPE'

    def get_mime_type(self):
        return self.kwargs.get(self.mime_type_kwarg, None)


class UserLogMixin(object):
    """ 用户日志记录 Mixin """

    success_def_msg = '操作成功'
    error_def_msg = '操作失败'

    def success_log(self, request, action_object, action_handler, status_note=None):
        """用户操作成功

        @param request: 当前请求
        @param action_object: 操作的对象
        @param action_handler:操作的处理函数
        @param status_note: 状态说明
        """

        user_log_success.send(sender=self, request=request, action_class=self.__doc__ or self.__class__,
                              action_object=str(action_object), action_handler=action_handler.__name__, status_note=status_note or self.success_def_msg)

    def error_log(self, request, action_object, action_handler, status_note=None):
        """用户操作失败

        @param request: 当前请求
        @param action_object: 操作的对象
        @param action_handler:操作的处理函数
        @param status_note: 状态说明
        """

        user_log_error.send(sender=self, request=request, action_class=self.__doc__ or self.__class__,
                            action_object=str(action_object), action_handler=action_handler.__name__, status_note=status_note or self.error_def_msg)
