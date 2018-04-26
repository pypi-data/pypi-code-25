# -*- coding: utf-8 -*-
from zebe.module.remind import Remind, RemindModelSession
from zebe.service.base import ModelBaseService


# 提醒服务
class RemindService(ModelBaseService):

    def __init__(self):
        super().__init__(Remind, RemindModelSession)
