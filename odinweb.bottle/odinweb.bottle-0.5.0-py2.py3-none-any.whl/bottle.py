"""
OdinWeb.Bottle API
~~~~~~~~~~~~~~~~~

Bottle implementation of the OdinWeb API interface.

Usage::
    
    import bottle
    from odinweb.bottle import Api
        
    app = bottle.Bottle()
    app.merge(
        Api(
            ApiVersion(
                UserApi(),
                version='v1
            )
        )
    )    

"""
from __future__ import absolute_import

from bottle import Route, response, request, BaseRequest

from odin.utils import lazy_property
from odinweb.containers import ApiInterfaceBase
from odinweb.constants import Type, Method, PATH_STRING_RE
from odinweb.data_structures import PathParam, MultiValueDict, BaseHttpRequest

# Imports for typing support
from typing import Iterator, List  # noqa


TYPE_MAP = {
    Type.Integer: 'int',
    Type.Long: 'int',
    Type.Float: 'float',
    Type.Double: 'float',
    Type.String: 're:' + PATH_STRING_RE,
    Type.Byte: '',
    Type.Binary: '',
    Type.Boolean: 'bool',
    Type.Date: 're:' + PATH_STRING_RE,
    Type.Time: 're:' + PATH_STRING_RE,
    Type.DateTime: 're:' + PATH_STRING_RE,
    Type.Password: 're:' + PATH_STRING_RE,
}


class RequestProxy(BaseHttpRequest):
    def __init__(self, r):
        # type: (BaseRequest) -> None
        self.request = r

    @lazy_property
    def environ(self):
        return self.request.environ

    @lazy_property
    def method(self):
        try:
            return Method(self.request.method)
        except KeyError:
            pass

    @lazy_property
    def scheme(self):
        return self.request.urlparts.scheme

    @lazy_property
    def host(self):
        return self.request.urlparts.netloc

    @lazy_property
    def path(self):
        return self.request.urlparts.path

    @lazy_property
    def query(self):
        return MultiValueDict(self.request.GET.allitems())

    @lazy_property
    def headers(self):
        return self.request.headers

    @lazy_property
    def cookies(self):
        return self.request.cookies

    @lazy_property
    def session(self):
        raise NotImplemented("Not supplied by Bottle")

    @lazy_property
    def body(self):
        return self.request.body.read()
    
    @lazy_property
    def form(self):
        return MultiValueDict(self.request.POST.allitems())


class Api(ApiInterfaceBase):
    def __iter__(self):
        # type: () -> Iterator[Route]
        """
        Iterator to simplify registration with Bottle using :func:`bottle.Bottle.merge`.
        """
        for url_path, operation in self.op_paths():
            path = url_path.format(self.node_formatter)
            for method in operation.methods:
                yield Route(self, path, method.value, self._bound_callback(operation))

    @staticmethod
    def node_formatter(path_node):
        # type: (PathParam) -> str
        """
        Format a node to be consumable by the `UrlPath.parse`.
        """
        if path_node.type:
            node_type = TYPE_MAP.get(path_node.type, 'str')
            return "<{}:{}>".format(path_node.name, node_type)
        return "<{}>".format(path_node.name)

    @property
    def plugins(self):
        # type: () -> list
        # Placeholder to match the Bottle App API.
        return []

    @property
    def routes(self):
        # type: () -> List[Route]
        return list(self)

    def _bound_callback(self, operation):
        """
        Bind operation into method for translating between OdinWeb and Bottle.
        """
        def callback(**path_args):
            # Dispatch incoming request after applying proxy to request object
            resp = self.dispatch(operation, RequestProxy(request), **path_args)

            # Translate standard OdinWeb response into Bottle response.
            response.status = resp.status
            for k, v in resp.headers.items():
                response[k] = v

            return resp.body
        return callback
