# -*- coding: utf-8 -*-


"""
Id                   KeyId                not null,
User_Id              VARCHAR(36)          not null,
Action_Flag          INT2                 not null,
Action_Time          TIMESTAMP            not null,
Action_Class         TEXT                 not null,
Action_Object        TEXT                 not null,
Action_Handler       VARCHAR(200)         not null,
IP                   VARCHAR(32)          not null,
Status               INT2                 not null,
Status_Note          TEXT                 null,
constraint PK_AUTH_USER_LOG primary key (Id)
"""

import uuid

from bigtree_api.models.auth_user_log import AuthUserLogModel


class ModelBackend(object):

    def record(self, user_id, action_flag, action_time, action_class, action_object, action_handler, ip, status, status_note=None):
        entity = {
            'id': uuid.uuid4(),
            'user_id': user_id,
            'action_flag': action_flag,
            'action_time': action_time,
            'action_class': action_class,
            'action_object': action_object,
            'action_handler': action_handler,
            'ip': ip,
            'status': status,
            'status_note': status_note
        }
        service = AuthUserLogModel()
        service.add(entity)


class MQTTBackend(object):

    def record(self, user_id, action_flag, action_time, action_class, action_object, action_handler, ip, status, status_note=None):
        raise NotImplementedError


class CeleryBackend(object):

    def record(self, user_id, action_flag, action_time, action_class, action_object, action_handler, ip, status, status_note=None):
        raise NotImplementedError
