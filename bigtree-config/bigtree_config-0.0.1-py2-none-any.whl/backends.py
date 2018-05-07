# -*- coding: utf-8 -*-

"""
create table Sys_Config (
   Config_Key           VARCHAR(20)          not null,
   Config_Value         TEXT                 not null,
   Config_Name          VARCHAR(200)         not null,
   constraint PK_SYS_CONFIG primary key (Config_Key)
);
"""


from bigtree_api.models.sys_config import SysConfigModel


class ModelBackend(object):

    def get_config(self):
        service = SysConfigModel()
        return service.get_all()
