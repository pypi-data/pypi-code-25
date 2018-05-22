# -*- coding: utf-8 -*-

"""
    message_media_webhooks.message_media_webhooks_client

    This file was automatically generated for MessageMedia by APIMATIC v2.0 ( https://apimatic.io ).
"""
from .decorators import lazy_property
from .configuration import Configuration
from .controllers.webhooks_controller import WebhooksController

class MessageMediaWebhooksClient(object):

    config = Configuration

    @lazy_property
    def webhooks(self):
        return WebhooksController()


    def __init__(self, 
                 basic_auth_user_name = None,
                 basic_auth_password = None):
        if basic_auth_user_name != None:
            Configuration.basic_auth_user_name = basic_auth_user_name
        if basic_auth_password != None:
            Configuration.basic_auth_password = basic_auth_password


