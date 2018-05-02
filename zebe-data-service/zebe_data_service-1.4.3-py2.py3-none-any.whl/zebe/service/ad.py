# -*- coding: utf-8 -*-
from zebe.module.ad import Ad, AdModelSession
from zebe.service.base import ModelBaseService


# 广告服务
class AdService(ModelBaseService):

    def __init__(self):
        super().__init__(Ad, AdModelSession)
