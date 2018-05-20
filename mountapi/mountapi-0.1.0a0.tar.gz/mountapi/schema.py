import abc
import inspect
import re

from mountapi.core import exceptions


class AbstractConverter(metaclass=abc.ABCMeta):
    param_url: str = None
    param_regex: str = None

    @classmethod
    def path_to_regex(cls, path):
        return re.sub(cls.param_url, cls.param_regex, path) + '$'


class IntConverter(AbstractConverter):
    param_url = r'<(?P<param>\w+):int>'
    param_regex = r'(?P<\1>\\d+)'


class StrConverter(AbstractConverter):
    param_url = r'<(?P<param>\w+):str>'
    param_regex = r'(?P<\1>\\w+)'


class AbstractSchema(exceptions.NotImplementedMixin, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def build(self):
        raise self.not_implemented()

    @abc.abstractmethod
    def match(self, path: str, method: str):
        raise self.not_implemented()


class Schema(AbstractSchema):
    _converter_map = {int: IntConverter, str: StrConverter}

    def __init__(self, routes: list) -> None:
        self._routes = routes
        self._schema = None

    def build(self) -> None:
        if self._schema is None:
            self._schema = self._build_schema()

    def _build_schema(self):
        schema = {}
        for route in self._routes:
            schema[route.path] = {
                'regex': self._get_path_regex(route.path),
                **self._get_schema_by_method(route)
            }
        return schema

    def _get_path_regex(self, path: str):
        for converter in self._converter_map.values():
            path = converter.path_to_regex(path)

        return path

    def _get_schema_by_method(self, route):
        return {
            method: {
                'handler': route.handler,
                'param_names': self._get_handler_param_names(route.handler),
            } for method in route.methods
        }

    def _get_handler_param_names(self, handler):
        param_values = inspect.signature(handler).parameters.values()
        return {
            param.annotation: param.name for param in param_values
        }

    def match(self, path: str, method: str):
        for route_path in self._schema:
            route_match = re.match(self._schema[route_path]['regex'], path)
            if route_match and method in self._schema[route_path]:
                return {
                    **self._schema[route_path][method],
                    'param_values': route_match.groupdict()
                }
