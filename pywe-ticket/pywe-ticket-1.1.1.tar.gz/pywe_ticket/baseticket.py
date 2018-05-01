# -*- coding: utf-8 -*-

from pywe_token import BaseToken


class BaseTicket(BaseToken):
    def __init__(self, appid=None, secret=None, token=None, type='jsapi', storage=None, token_fetched_func=None, ticket_fetched_func=None):
        super(BaseTicket, self).__init__(appid=appid, secret=secret, token=token, storage=storage, token_fetched_func=token_fetched_func)
        self.type = type
        self.ticket_fetched_func = ticket_fetched_func

    def update_params(self, appid=None, secret=None, token=None, type='jsapi', storage=None, token_fetched_func=None, ticket_fetched_func=None):
        self.appid = appid or self.appid
        self.secret = secret or self.secret
        self.token = token or self.token
        self.type = type or self.type
        self.storage = storage or self.storage
        self.token_fetched_func = token_fetched_func or self.token_fetched_func
        self.ticket_fetched_func = ticket_fetched_func or self.ticket_fetched_func
