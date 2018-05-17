# -*- coding: utf-8 -*-
import asyncio
import logging
import inspect
import re
from typing import Callable, List, AnyStr, Dict, Tuple, Any

import httptools

from .request import Request
from .response import Response
from .exceptions import HttpException, UnknownSignalException
from .utils import HTTP_METHODS, STATUS_CODES, DEFAULT_ERROR_PAGE_TEMPLATE


logger = logging.getLogger('tendaysweb')
logging.basicConfig(level=logging.INFO)


class TenDaysWeb():
    _signal_types = ['run_before_start', 'run_after_close']

    def __init__(self, application_name):
        """
        :param application_name: just name your TenDaysWeb Instance
        """
        self._app_name = application_name
        self._rule_list: List[Rule] = []
        self._error_handlers: Dict[int, Callable] = {}
        self._signal_func: Dict[str, List[Callable]] = {
            key: []
            for key in TenDaysWeb._signal_types
        }

    def route(self, url: str, methods: List = HTTP_METHODS, **options):
        """
            A decorator that is used to register a view function for a
        given URL rule.  Example::

            @app.route('/')
            def index():
                return 'Hello World'
        """
        def decorator(func):
            self._rule_list.append(Rule(url, methods, func, **options))
            return func
        return decorator

    def signal(self, signal_type: str):
        """
            A decorator that is used to register a function supposed to be called
            before start_server
        """
        def decorator(func):
            if signal_type not in TenDaysWeb._signal_types:
                raise UnknownSignalException(signal_type, func.__name__)
            self._signal_func[signal_type].append(func)
            return func
        return decorator

    def error_handler(self, error_code):
        """
        This decorator is used to customize the behavior of an error
        :param error_code:a http status code
        """
        async def decorator(func):
            self._error_handlers[error_code] = func
            return func
        return decorator

    def match_request(self, request) -> Tuple[Callable, Dict[str, Any]]:
        """
        Match each request to a endpoint
        if no endpoint is eligable, return None, None
        """
        handler = kwargs = None
        for rule in self._rule_list:
            kwargs = rule.match(request.url, request.method)
            if kwargs is not None:
                handler = rule._endpoint
                break
        return handler, kwargs

    async def process_request(
                            self,
                            request: Request,
                            handler: Callable,
                            kwargs: Dict[str, Any]):
        """
        :param request: Request instance
        :param handler: A endpoint
        :param kwargs: the additional parameters for call endpoint
        """
        try:
            return await handler(request, **kwargs)
        except HttpException as e:
            # catch exception user explicit rasie in endpoint
            handler = self._error_handlers.get(e.err_code, None)
            if handler is None:
                return Response(
                        status_code=e.err_code,
                        content=TenDaysWeb.generate_default_error_page(
                            e.err_code))
            return await handler()

    async def handler(self, reader, writer):
        """
        The handler handling each request
        :param request: the Request instance
        :return: The Response instance
        """
        while True:
            request: Request = await self.read_http_message(reader)
            response: Response = Response()

            if request is None:
                writer.close()
                break

            handler, kwargs = self.match_request(request)

            if handler is None:
                response.status_code = 404
                response.content = TenDaysWeb.generate_default_error_page(
                    response.status_code)
            else:
                try:
                    response = await self.process_request(
                        request, handler, kwargs)
                except Exception as e:
                    logger.error(str(e))
                    response = Response(
                        status_code=500,
                        content=TenDaysWeb.generate_default_error_page(500))

            # send payload
            writer.write(response.to_payload())

            try:
                await writer.drain()
                writer.write_eof()
            except ConnectionResetError:
                writer.close()
                break

    async def start_server(self,
                           loop,
                           http_handler: Callable,
                           websocket_handler=None,
                           address: str = 'localhost',
                           port: int=8000,):
        """
        start server
        """
        for func in self._signal_func['run_before_start']:
            if inspect.iscoroutinefunction(func):
                await func(loop)
            else:
                func()

        await asyncio.start_server(http_handler, address, port)

        for func in self._signal_func['run_after_close']:
            if inspect.iscoroutinefunction(func):
                await func(loop)
            else:
                func()

    def run(self,
            host: str = "localhost",
            port: int = 8000,
            debug: bool = False):
        """
        start the http server
        :param host: The listening host
        :param port: The listening port
        :param debug: whether it is in debug mod or not
        """
        loop = asyncio.get_event_loop()

        try:
            loop.run_until_complete(
                self.start_server(loop, self.handler, None, host, port))
            logger.info(f'Start listening {host}:{port}')
            loop.run_forever()
        except KeyboardInterrupt:
            loop.close()

    async def read_http_message(
            self, reader: asyncio.streams.StreamReader) -> Request:
        """
        this funciton will reading data cyclically
            until recivied a complete http message
        :param reqreaderuest: the asyncio.streams.StreamReader instance
        :return The Request instance
        """
        protocol = ParseProtocol()
        parser = httptools.HttpRequestParser(protocol)
        while True:
            data = await reader.read(2 ** 16)

            try:
                parser.feed_data(data)
            except httptools.HttpParserUpgrade:
                raise HttpException(400)

            if protocol.completed:
                return Request.load_from_parser(parser, protocol)
            if data == b'':
                return None

    @staticmethod
    def generate_default_error_page(status, reason='', content=''):
        return DEFAULT_ERROR_PAGE_TEMPLATE.format(
                            **{'status': status,
                                'reason': STATUS_CODES.get(status, 'Unknow'),
                                'content': content})


class Rule():
    parttern = re.compile(r'\<([^/]+)\>')

    def __init__(self, url: AnyStr, methods: List, endpoint: Callable,
                 **options):
        """
        A rule describes a url is expected to be handled and how to handle it.
        :param url: url to be handled
        :param method: list of HTTP method name
        :param endpoint: the actual function/class process this request
        """
        self._url = url
        self._methods = methods
        self._options = options
        self._endpoint = endpoint

        self._param_name_list = Rule.parttern.findall(url)
        self._url_pattern = re.compile(
            f'''^{Rule.parttern.sub('([^/]+)', url)}$''')

    def match(self, url: str, method: str):
        """
        this function is used to judge whether a (url, method) matchs the Rule
        """
        res = self._url_pattern.search(url)
        if method in self._methods and res is not None:
            return dict(zip(
                self._param_name_list,
                [res.group(i) for i in range(
                    1, self._url_pattern.groups + 1)]))
        return None


class ParseProtocol:
    """
    The protocol for HttpRequestParser
    """

    def __init__(self) -> None:
        self.url: str = ''
        self.headers: Dict[str, str] = {}
        self.body: bytes = b''
        self.completed: bool = False

    def on_url(self, url: bytes) -> None:
        self.url = url.decode()

    def on_header(self, name: bytes, value: bytes) -> None:
        self.headers[name.decode()] = value.decode()

    def on_body(self, body: bytes) -> None:
        self.body += body

    def on_message_complete(self) -> None:
        self.completed = True
