from asyncio.selector_events import _SelectorSocketTransport
from typing import Callable, Optional
import asyncio

import httptools

from mountapi.http.request import Request
from mountapi.http.response import Response
from mountapi.lib import json


class Server:
    def __init__(self, transport: _SelectorSocketTransport,
                 request_handler: Callable):
        self._loop = asyncio.get_event_loop()
        self._parser = httptools.HttpRequestParser(self)
        self._transport: _SelectorSocketTransport = transport
        self._request: Request = None
        self._request_handler: Callable = request_handler

    def data_received(self, data: bytes) -> None:
        self._parser.feed_data(data)

    def on_message_begin(self):
        self._request = Request()
        self._request.method = self._parser.get_method().decode()

    def on_url(self, url: bytes):
        self._request.parse_url(url)

    def on_body(self, body: bytes):
        self._request.POST = json.loads(body)

    def on_message_complete(self):
        task = asyncio.ensure_future(self._request_handler(self._request))
        task.add_done_callback(self._finish_response)

    def eof_received(self) -> bool:
        return True

    def _finish_response(self, task):
        response: Response = Response.from_result(task.result())
        self._write(response.to_bytes())
        self._transport.close()

    def _write(self, msg: bytes):
        self._transport.write(msg)


class ServerProtocol(asyncio.Protocol):
    def __init__(self, request_handler: Callable):
        self._request_handler = request_handler
        self._server: Optional[Server] = None

    def connection_made(self, transport: _SelectorSocketTransport) -> None:
        self._server: Optional[Server] = Server(
            transport, self._request_handler
        )

    def data_received(self, data: bytes) -> None:
        self._server.data_received(data)

    def eof_received(self) -> bool:
        return self._server.eof_received()
