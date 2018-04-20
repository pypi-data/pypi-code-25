# coding: utf-8

import json
import yaml
import typing
import functools
import posixpath
from copy import deepcopy
from jsonschema import validate
from .common import RULE_JSON_SCHEMA

SUPPORTED_METHODS = ("get", "post", "put", "delete", "path")


IdType = typing.Union[int, str]
BodyType = typing.Union[str, bytes, list, dict]


class Rule(object):
    class resource(object):
        def __init__(self, path: str):
            self.path = path

        def _request(self, method: str, id: IdType=None, *args, **kwargs) -> "Rule":
            path = self.path
            if id is not None:
                path = posixpath.join(path, str(id))
            return Rule.request(method, path, *args, **kwargs)

        def __getattr__(self, item):
            return functools.partial(self._request, item)

    @classmethod
    def request(cls, method: str, path: str, queries: dict=None, headers: dict=None, body: BodyType=None,
                id: IdType=None, description: str=None
                ) -> "Rule":
        method = method.lower()
        assert method in SUPPORTED_METHODS

        request = {
            "method": method,
            "path": path,
        }

        if queries is not None:
            request["queries"] = queries

        if headers is not None:
            request["headers"] = headers

        if body is not None:
            request["body"] = body

        obj = cls(request, id=id, description=description)
        return obj

    get = functools.partialmethod(request, "get")
    post = functools.partialmethod(request, "post")
    put = functools.partialmethod(request, "put")
    delete = functools.partialmethod(request, "delete")
    patch = functools.partialmethod(request, "patch")

    def __init__(self, request: dict, response: dict=None, id: IdType=None, description: str=None):
        self._request = request
        self._request["method"] = self._request["method"].lower()
        self._response = response
        self.id = id
        self.description = description

    def response(self, body: BodyType=None, status: int=200, headers: dict=None, delay: typing.Union[float, int]=None) -> "Rule":
        resp = {}

        if body is not None:
            resp["body"] = body

        if status is not None:
            resp["status"] = status

        if headers is not None:
            resp["headers"] = headers

        if delay is not None:
            resp["delay"] = delay

        self._response = resp
        return self

    def as_dict(self) -> dict:
        data = {
            "request": self._request
        }
        if self.id is not None:
            data["id"] = self.id

        if self.description is not None:
            data["description"] = self.description

        data["response"] = self._response or {}
        return data

    @classmethod
    def from_dict(cls, d: dict):
        validate(d, RULE_JSON_SCHEMA)
        return cls(**d)

    @classmethod
    def from_json(cls, j):
        if hasattr(j, "read"):
            d = json.load(j)
        else:
            d = json.loads(j)
        return cls.from_dict(d)

    @classmethod
    def from_yaml(cls, y):
        d = yaml.load(y)
        return cls.from_dict(d)

    def copy(self):
        return self.__class__(**deepcopy(self.as_dict()))
