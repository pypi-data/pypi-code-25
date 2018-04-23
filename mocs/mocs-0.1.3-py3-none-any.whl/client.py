# coding: utf-8

import sys
import socket
import errno
import inspect
import typing
import functools
import posixpath

import requests
from requests.compat import urlunparse

import unittest.mock
from .common import RULE_API_REST_BASE_PATH, DEFAULT_HTTP_BIND, DEFAULT_HTTP_HOST, DEFAULT_HTTP_PORT
from .rule import Rule
from .server.app import AppProcess

import logging
logger = logging.getLogger(__name__)


class MockError(Exception):
    pass


def run_server_in_subprocess(host: str=DEFAULT_HTTP_BIND, port: int=DEFAULT_HTTP_PORT, config: str=None):
    process = AppProcess(port, host, config)
    process.start()
    return process


class _HttpSession(requests.Session):
    @staticmethod
    def pformat(headers):
        return "\n".join(["%s: %s" % (key, value) for key, value in headers.items()])

    def send(self, request, **kwargs):
        logger.debug('Http Request: "%s %s"\n%s\n\n%s', request.method, request.url, self.pformat(request.headers), request.body or "")
        resp = requests.Session.send(self, request, **kwargs)
        logger.debug("Http Response: %s\n%s\n\n%s", resp.status_code, self.pformat(resp.headers), resp.text or "")
        if not resp.ok:
            raise MockError(resp.reason)
        return resp


class _HttpMockServer(object):
    class _Request(object):
        def __init__(self, server: "_HttpMockServer", *args, **kwargs):
            self.server = server
            self.rule = Rule.request(*args, **kwargs)

        def response(self, *args, **kwargs):
            self.rule.response(*args, **kwargs)
            return self.server.new_rule(self.rule)

    def __init__(self, host: str=DEFAULT_HTTP_HOST, port: int=DEFAULT_HTTP_PORT):

        self.host = host
        self.port = port

    def request(self, *args, **kwargs) -> _Request:
        return self._Request(self, *args, **kwargs)

    get = functools.partialmethod(request, "get")
    post = functools.partialmethod(request, "post")
    put = functools.partialmethod(request, "put")
    delete = functools.partialmethod(request, "delete")
    patch = functools.partialmethod(request, "patch")

    def new_rule(self, rule: typing.Union[dict, Rule]) -> "HttpMock":
        if isinstance(rule, dict):
            rule = Rule.from_dict(rule)
        data = rule.as_dict()

        netloc = "{}:{}".format(self.host, self.port)
        api_root_url = urlunparse(("http", netloc, RULE_API_REST_BASE_PATH, '', '', ''))
        with _HttpSession() as session:
            resp = session.post(api_root_url, json=data)

        rule_id = resp.json()["id"]
        return HttpMock(rule_id, self.host, self.port)


class HttpMock(object):
    Server = _HttpMockServer

    def __init__(self, rule_id: str, host: str=DEFAULT_HTTP_HOST, port: int=DEFAULT_HTTP_PORT):
        self.netloc = "{}:{}".format(host, port)
        rule_path = posixpath.join(RULE_API_REST_BASE_PATH, rule_id)
        self.url = urlunparse(("http", self.netloc, rule_path, '', '', ''))
        self._session = _HttpSession()

    @property
    def data(self):
        return self.get()

    def __call__(self):
        request = self.data["request"]
        path = request["path"]
        kwargs = {
            "params": request.get("queries", None),
            "headers": request.get("headers", None),
        }
        body = request.get("body", None)
        if isinstance(body, (list, dict)):
            kwargs["json"] = body
        elif isinstance(body, (str, bytes)):
            kwargs["data"] = body
        else:
            pass
        url = urlunparse(("http", self.netloc, path, '', '', ''))
        return self._session.request(request["method"], url, **kwargs)

    def get(self) -> dict:
        resp = self._session.get(self.url)
        return resp.json()

    def update(self, rule: dict, merge: bool=False) -> None:
        params = {"merge": merge} if merge else {}
        self._session.put(self.url, params=params, json=rule)

    def reset(self) -> None:
        params = {"reset": True}
        self._session.put(self.url, params=params)

    def delete(self) -> None:
        self._session.delete(self.url)
        self._session.close()

    @property
    def call_count(self) -> int:
        data = self.get()
        return data["called"]["times"]

    @property
    def called(self) -> bool:
        count = self.call_count
        return bool(count)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.delete()


class mock_server(object):
    def __init__(self, rule: typing.Union[dict, Rule], auto_start=False, **kwargs):
        self.rule = rule
        self.auto_start = auto_start
        self.kwargs = inspect.getcallargs(_HttpMockServer, None, **kwargs)
        self.kwargs.pop("self")
        self.mock = None
        self.server = None

    def decorate_class(self, klass):
        for attr in dir(klass):
            if attr.startswith(unittest.mock.patch.TEST_PREFIX):
                attr_value = getattr(klass, attr)
                if hasattr(attr_value, "__call__"):
                    setattr(klass, attr, self.decorate_func(attr_value))
        return klass

    def decorate_func(self, func):
        if hasattr(func, 'mocs_stubs'):
            func.mocs_stubs.append(self)
            return func

        @functools.wraps(func)
        def patched(*args, **kwargs):
            extra_args = []
            entered_patchers = []

            exc_info = tuple()
            try:
                for patcher in patched.mocs_stubs:
                    arg = patcher.__enter__()
                    entered_patchers.append(patcher)
                    extra_args.append(arg)
                args += tuple(extra_args)

                return func(*args, **kwargs)
            except:
                exc_info = sys.exc_info()
                raise
            finally:
                for patcher in reversed(entered_patchers):
                    patcher.__exit__(*exc_info)

        patched.mocs_stubs = [self]
        return patched

    def __call__(self, item):
        if inspect.isclass(item):
            return self.decorate_class(item)
        return self.decorate_func(item)

    def __enter__(self) -> HttpMock:
        if self.auto_start:
            self.start_server()
        server = _HttpMockServer(**self.kwargs)
        self.mock = server.new_rule(self.rule)
        return self.mock

    def __exit__(self, *exc_info):
        try:
            self.mock.delete()
        finally:
            if self.auto_start and self.server is not None:
                self.server.stop()
                self.server = None

    def start_server(self):
        host = self.kwargs["host"]
        port = self.kwargs["port"]
        sock = socket.socket()
        try:
            sock.bind((host, port))
        except socket.error as err:
            sock.close()
            logger.warn(str(err))
            if err.errno != errno.EADDRINUSE:
                raise
        else:
            sock.close()
            self.server = run_server_in_subprocess(host, port)

    def start(self) -> HttpMock:
        return self.__enter__()

    def stop(self):
        self.__exit__()



