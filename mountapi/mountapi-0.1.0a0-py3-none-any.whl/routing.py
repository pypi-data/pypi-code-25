import abc
from typing import Callable

from mountapi.core import exceptions
from mountapi.http.exceptions import Http404
from mountapi.schema import AbstractSchema


class Route:
    def __init__(self, path, handler, methods=None) -> None:
        self.path = path
        self.handler = handler
        self.methods = methods or ['GET']


class AbstractRouter(exceptions.NotImplementedMixin, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def dispatch(self, path: str, method: str) -> Callable:
        raise self.not_implemented()


class Router(AbstractRouter):
    def __init__(self, schema: AbstractSchema) -> None:
        self._schema: AbstractSchema = schema

    async def dispatch(self, path: str, method: str) -> Callable:
        result = self._schema.match(path, method)
        if not result:
            raise Http404()

        return result
