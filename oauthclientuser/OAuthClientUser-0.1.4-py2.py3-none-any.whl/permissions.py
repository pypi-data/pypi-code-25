# -*- coding: utf-8 -*-
from rest_framework.permissions import BasePermission


def oauth2_remote_permission(privilege):
    class Permission(BasePermission):
        def has_permission(self, request, view):
            if not hasattr(request.user, 'extra'):
                return False
            else:
                remote_privileges = request.user.extra.remote_privileges
                remote_privilege_list = remote_privileges.split('|')

                return privilege in remote_privilege_list

    return Permission
