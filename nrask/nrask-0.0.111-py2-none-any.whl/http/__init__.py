from nrask.base import Base
from tornado.web import asynchronous,RequestHandler
from tornado.websocket import WebSocketHandler

__all__ = [
    'asynchronous'
    'Handler',
    'WSHandler'
]

class Handler(RequestHandler,Base):
    def set_default_headers(self):
        self.set_header('Server','Viking Makt HTTP Server')

class WSHandler(WebSocketHandler,Base):
    def check_origin(self,origin):
        return True
