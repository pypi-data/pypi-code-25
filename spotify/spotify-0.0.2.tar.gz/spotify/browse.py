##
# -*- coding: utf-8 -*-
##

class Browse:
    __slots__ = ['_client', 'categories']

    def __init__(self, client):
        self._client = client

    def __aenter__(self):
        return self

    def __aexit__(self, *args, **kwargs):
        pass
