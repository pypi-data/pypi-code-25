import time
from wsgiref.handlers import format_date_time

from mountapi.http import status
from mountapi.lib import json


class Response:
    def __init__(self, content, status_code=None):
        if isinstance(content, str):
            self._content = content.encode()
        else:
            self._content = json.dumps(content).encode()
        self._status_code = status_code or status.OK_200

    @classmethod
    def from_result(cls, result):
        if isinstance(result, Response):
            return result
        else:
            return Response(result)

    def to_bytes(self):
        return (
            b'HTTP/1.1 %i %b\r\n'
            b'Date: %b\r\n'
            b'Connection: closed\r\n'
            b'Content-Type: application/json\r\n\r\n'
            b'%b' % (
                self._status_code['code'], self._status_code['reason'],
                format_date_time(time.time()).encode(),
                self._content,
            )
        )
