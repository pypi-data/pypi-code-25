# -*- coding: utf-8 -*-
from zebe.module.app import App, AppModelSession
from zebe.service.base import ModelBaseService


# 应用服务
class AppService(ModelBaseService):

    def __init__(self):
        super().__init__(App, AppModelSession)
