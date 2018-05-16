# -*- coding: utf-8 -*-
from typing import Dict

from .utils import STATUS_CODES


class Response:
    def __init__(self,
                 status_code: int = 200,
                 headers: Dict[str, str] = {},
                 content='',
                 options: Dict[str, str] = {}):
        self.status_code = status_code
        self.headers = headers
        self.content = content
        self.reason_phrase = options.get('reason_phrase',
                                         STATUS_CODES.get(
                                             self.status_code,
                                             'Unknown Error'))

    def to_payload(self):
        response: bytes = \
            f'HTTP/1.1 {self.status_code} {self.reason_phrase}\r\n'.encode()
        for k, v in self.headers.items():
            response += f'{k}: {v}\r\n'.encode()
        response += b'\r\n'
        response += self.content.encode()
        return response
