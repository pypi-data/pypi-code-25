# coding: utf-8

import sys
import socket
import errno
import inspect
import typing
import functools
import posixpath

import requests
from requests.compat import urljoin

import unittest.mock
from .common import RULE_API_REST_BASE_PATH, DEFAULT_HTTP_BIND, DEFAULT_HTTP_HOST, DEFAULT_HTTP_PORT
from .rule import Rule
from .server.app import AppProcess

import logging
logger = logging.getLogger(__name__)


class MockError(Exception):
    pass


class HttpSession(requests.Session):
    @staticmethod
    def pformat(headers):
        return "\n".join(["%s: %s" % (key, value) for key, value in headers.items()])

    def send(self, request, **kwargs):
        logger.debug('Http Request: "%s %s"\n%s\n\n%s', request.method, request.url, self.pformat(request.headers), request.body or "")
        resp = requests.Session.send(self, request, **kwargs)
        logger.debug("Http Response: %s\n%s\n\n%s", resp.status_code, self.pformat(resp.headers), resp.text or "")
        return resp


def _check_ok(resp):
    if not resp.ok:
        raise MockError(resp.reason)


class RuleMock(object):
    def __init__(self, url: str, data: dict):
        self.url = url
        self.data = data
        self.session = HttpSession()

    def get(self, params: dict=None) -> dict:
        params = params or {}
        resp = self.session.get(self.url, params=params)
        _check_ok(resp)
        return resp.json()

    def update(self, rule: dict, merge: bool=False) -> None:
        params = {"merge": merge} if merge else {}
        resp = self.session.put(self.url, params=params, json=rule)
        _check_ok(resp)

    def reset(self) -> None:
        params = {"reset": True}
        resp = self.session.put(self.url, params=params)
        _check_ok(resp)

    def delete(self) -> None:
        resp = self.session.delete(self.url)
        _check_ok(resp)

    @property
    def call_count(self) -> int:
        data = self.get()
        return data["called"]["times"]

    @property
    def called(self) -> bool:
        count = self.call_count
        return bool(count)

    def assert_not_called(self):
        raise NotImplementedError

    def assert_has_calls(self, calls, any_order=False):
        raise NotImplementedError


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
            raise MockError(resp.reason)

        api_rule_url = posixpath.join(api_root_url, resp.json()["id"])
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
        # import time
        # time.sleep(60)
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

    def start(self) -> RuleMock:
        return self.__enter__()

    def stop(self):
        self.__exit__()



