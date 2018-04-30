# -*- coding: utf-8 -*-
from zebe.module.cdrvba import CorelDrawVBASubscriber, CorelDrawVBASubscriberModelSession
from zebe.service.base import ModelBaseService


# CorelDRAW VBA订阅用户
class CorelDrawVBASubscriberService(ModelBaseService):

    def __init__(self):
        super().__init__(CorelDrawVBASubscriber, CorelDrawVBASubscriberModelSession)
