# -*- coding: utf-8 -*-
import socket

from maple import constants as maple_constants
from ..log import logger
from .. import constants


def catch_exc(func):
    import functools

    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            logger.error('exc occur.', exc_info=True)

    return func_wrapper


class Client(object):

    sock = None

    app = None
    host = None
    port = None
    # 排除的cmd列表
    exclude = None
    # 是否保持原样，即是否包括body
    raw = None

    def __init__(self, app=None, config=None):
        # 一开始就创建好sock
        self._create_socket()

        if app:
            self.init_app(app, config)

    def init_app(self, app, config=None):
        """
        :param app:
        :param config: dict(host=127.0.0.1, port=3333)
        :return:
        """
        self.app = app
        config = config or dict()

        self.host = config.get('host') or constants.HOST
        self.port = config.get('port') or constants.PORT
        self.exclude = config.get('exclude')
        self.raw = config.get('raw') or False

        @app.before_request
        @app.create_client
        @catch_exc
        def upload_data(request):
            if request.task.cmd not in (maple_constants.CMD_CLIENT_CREATED, maple_constants.CMD_CLIENT_REQ):
                return

            if request.task.cmd == maple_constants.CMD_CLIENT_REQ:
                if self.exclude and request.box.cmd in self.exclude:
                    return

            body = request.task.body
            data = None
            try:
                if not self.raw:
                    request.task.body = ''
                data = request.task.pack()
            finally:
                if not self.raw:
                    request.task.body = body

            if data:
                self.send(data)

    def send(self, data):
        """
        发送
        """
        self.sock.sendto(data, (self.host, self.port))

    def _create_socket(self):
        """
        创建socket
        """
        # 先尝试关闭掉
        self.close()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(0)

    def close(self):
        """
        关闭
        """
        if self.sock is None:
            return

        try:
            self.sock.close()
        except:
            pass
        finally:
            self.sock = None
