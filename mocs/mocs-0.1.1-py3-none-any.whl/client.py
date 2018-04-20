# coding: utf-8

import sys
import socket
import errno
import inspect
import typing
import functools

import requests
from requests.compat import urljoin

import unittest.mock
from .common import RULE_API_REST_BASE_PATH, DEFAULT_HTTP_BIND, DEFAULT_HTTP_HOST, DEFAULT_HTTP_PORT
from .rule import Rule
from .server.app import AppProcess

import logging
logger = logging.getLogger(__name__)


class ClientError(Exception):
    pass


class RuleMock(object):
    def __init__(self, url: str, data: dict):
        self.url = url
        self.data = data

    def get(self):
        resp = requests.get(self.url)
        if not resp.ok:
            raise ClientError
        return resp.json()

    def reset(self):
        pass

    def delete(self):
        pass

    def assert_called(self, times):
        data = self.get()
        assert data["called"] == times


class _Request(object):
    def __init__(self, mock: "HttpMockClient", *args, **kwargs):
        self.mock = mock
        self.rule = Rule.request(*args, **kwargs)

    def response(self, *args, **kwargs):
        self.rule.response(*args, **kwargs)
        self.mock.new_rule(self.rule)


class HttpMockClient(object):
    def __init__(self, host: str=DEFAULT_HTTP_HOST, port: int=DEFAULT_HTTP_PORT, secure: bool=False):
        protocol = "https" if secure else "http"
        self.url = "{}://{}:{}".format(protocol, host, port)

    def request(self, *args, **kwargs) -> _Request:
        return _Request(self, *args, **kwargs)

    get = functools.partialmethod(request, "get")
    post = functools.partialmethod(request, "post")
    put = functools.partialmethod(request, "put")
    delete = functools.partialmethod(request, "delete")
    patch = functools.partialmethod(request, "patch")

    def new_rule(self, rule: typing.Union[dict, Rule]) -> RuleMock:
        if isinstance(rule, dict):
            rule = Rule.from_dict(rule)
        data = rule.as_dict()
        api_root_url = urljoin(self.url, RULE_API_REST_BASE_PATH)
        resp = requests.post(api_root_url, json=data)
        if not resp.ok:
            raise ClientError

        api_rule_url = urljoin(api_root_url, resp.json()["id"])
        return RuleMock(api_rule_url, data)


def run_server_in_subprocess(host: str=DEFAULT_HTTP_BIND, port: int=DEFAULT_HTTP_PORT, config: str=None):
    process = AppProcess(port, host, config)
    process.start()
    return process


class mock_server(object):
    def __init__(self, rule: typing.Union[dict, Rule], auto_start=False, **kwargs):
        self.rule = rule
        self.auto_start = auto_start
        self.kwargs = inspect.getcallargs(HttpMockClient, None, **kwargs)
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
                logger.exception("")
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

    def __enter__(self) -> RuleMock:
        if self.auto_start:
            self.start_server()
        client = HttpMockClient(**self.kwargs)
        self.mock = client.new_rule(self.rule)
        return self.mock

    def __exit__(self, *exc_info):
        self.mock.delete()
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

    def start(self) -> RuleMock:
        return self.__enter__()

    def stop(self):
        self.__exit__()



