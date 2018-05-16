# -*- coding: utf-8 -*-
from typing import Dict


class Request:
    def __init__(self, method: str, url: str, version: str,
                 headers: Dict[str, str], content: str):
        self.method = method
        self.url = url
        self.version = version
        self.headers = headers
        self.content = content

    @classmethod
    def load_from_parser(cls, parser: 'HttpRequestParser',
                         protocol: 'ParseProtocol') -> 'Request':
        return cls(
                parser.get_method().decode(),
                protocol.url,
                parser.get_http_version(),
                protocol.headers, protocol.body)
