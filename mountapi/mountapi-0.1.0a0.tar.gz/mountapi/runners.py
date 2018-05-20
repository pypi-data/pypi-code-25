import abc
import asyncio
import functools
import os
import sys
from typing import Type

from mountapi.contrib.output import write_stdout
from mountapi.core.settings import AbstractSettings
from mountapi.http.request import Request
from mountapi.reloaders import async_should_reload
from mountapi.server import ServerProtocol


class AbstractRunner(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def run(self) -> None:
        pass


class AsyncRunner(AbstractRunner):
    def __init__(self, settings: Type[AbstractSettings]) -> None:
        self._settings = settings

    def run(self) -> None:
        loop = asyncio.get_event_loop()
        create_server = loop.create_server(
            functools.partial(
                ServerProtocol,
                self._request_handler(),
            ),
            host=self._settings.host,
            port=self._settings.port
        )
        server = loop.run_until_complete(create_server)

        write_stdout(f'Serving on {server.sockets[0].getsockname()}')
        try:
            if self._settings.use_reloader:
                loop.run_until_complete(async_should_reload())
                server.close()
                loop.run_until_complete(server.wait_closed())

                write_stdout('Reloading server due to recent change.')
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                loop.run_forever()
        except KeyboardInterrupt:
            write_stdout('Keyboard Interrupt intercepted - shutdown.')
        finally:
            server.close()
            loop.run_until_complete(server.wait_closed())
            loop.close()

    def _request_handler(self):
        async def request_handler(request: Request):
            dispatch_result = await self._settings.router.dispatch(
                request.path, request.method
            )
            handler = dispatch_result['handler']
            handler_kwargs = dispatch_result['param_values']

            for param_name in dispatch_result['param_names'].items():
                if param_name[0] == Request:
                    handler_kwargs[param_name[1]] = request

            response = await handler(**handler_kwargs)
            return response
        
        return request_handler
