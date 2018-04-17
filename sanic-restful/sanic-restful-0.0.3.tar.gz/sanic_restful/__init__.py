from __future__ import absolute_import
import asyncio
from collections import Mapping
import operator
from functools import wraps, partial

from types import MethodType

from sanic import Blueprint, Sanic, request
from sanic.blueprints import FutureException
from sanic.exceptions import (SanicException, NotFound,
                              ServerError, abort as
                              original_sanic_abort)
from sanic.response import HTTPResponse as ResponseBase, text
from sanic.views import HTTPMethodView

from sanic_restful.exceptions import MethodNotAllowed, NotAcceptable
from sanic_restful.handlers import RestfulErrorHandle
from sanic_restful.representations.json import output_json
from sanic_restful.utils import (unpack, OrderedDict,
                                 best_match_accept_mimetype,
                                 _endpoint_from_view_func)

__all__ = ('Api', 'Resource', 'marshal', 'marshal_with', 'marshal_with_field',
           'abort')


def abort(http_status_code, **kwargs):
    """Raise a SanicException for the given http_status_code. Attach any keyword
    arguments to the exception for later processing.
    """
    # noinspection PyUnresolvedReferences
    try:
        original_sanic_abort(http_status_code)
    except SanicException as e:
        if len(kwargs):
            e.data = kwargs
        raise


DEFAULT_REPRESENTATIONS = [('application/json', output_json)]


class Api(object):
    """
    The main entry point for the application.
    You need to initialize it with a Flask Application: ::

    >>> app = Flask(__name__)
    >>> api = restful.Api(app)

    Alternatively, you can use :meth:`init_app` to set the Flask application
    after it has been constructed.

    :param app: the Flask application object
    :type app: flask.Flask or flask.Blueprint
    :param prefix: Prefix all routes with a value, eg v1 or 2010-04-01
    :type prefix: str
    :param default_mediatype: The default media type to return
    :type default_mediatype: str
    :param decorators: Decorators to attach to every resource
    :type decorators: list
    :param catch_all_404s: Use :meth:`handle_error`
        to handle 404 errors throughout your app
    :param serve_challenge_on_401: Whether to serve a challenge response to
        clients on receiving 401. This usually leads to a username/password
        popup in web browers.
    :param url_part_order: A string that controls the order that the pieces
        of the url are concatenated when the full url is constructed.  'b'
        is the blueprint (or blueprint registration) prefix, 'a' is the api
        prefix, and 'e' is the path component the endpoint is added with
    :type catch_all_404s: bool
    :param errors: A dictionary to define a custom response for each
        exception or error raised during a request
    :type errors: dict

    """

    def __init__(self,
                 app=None,
                 prefix='',
                 default_mediatype='application/json',
                 decorators=None,
                 catch_all_404s=False,
                 serve_challenge_on_401=False,
                 url_part_order='bae',
                 errors=None):
        self.representations = OrderedDict(DEFAULT_REPRESENTATIONS)
        self.urls = {}
        self.prefix = prefix
        self.default_mediatype = default_mediatype
        self.decorators = decorators if decorators else []
        self.catch_all_404s = catch_all_404s
        self.serve_challenge_on_401 = serve_challenge_on_401
        self.url_part_order = url_part_order
        self.errors = errors or {}
        self.error_handler = RestfulErrorHandle(
            errors, self.make_response, self.unauthorized, self.representation)
        self.blueprint_setup = None
        self.endpoints = set()
        self.resources = []
        self.app = None
        self.blueprint = None

        if app is not None:
            self.app = app
            self.init_app(app)

    def init_app(self, app):
        """Initialize this class with the given :class:`flask.Flask`
        application or :class:`flask.Blueprint` object.

        :param app: the Flask application or blueprint object

        Examples::

            api = Api()
            api.add_resource(...)
            api.init_app(app)

        """
        # If app is a blueprint, defer the initialization
        if isinstance(app, Blueprint):
            self.blueprint = app
            app.old_register = app.register
            app.register = self._sanic_blueprint_register_hack(app)
            self.exc_register(self.error_handler, self.errors, blueprint=app)
        elif isinstance(app, Sanic):
            self._init_app(app)
            self.exc_register(self.error_handler, self.errors, app=app)
        else:
            raise TypeError('only support sanic object and blupirint')

    def _complete_url(self, url_part, registration_prefix):
        """This method is used to defer the construction of the final url in
        the case that the Api is created with a Blueprint.

        :param url_part: The part of the url the endpoint is registered with
        :param registration_prefix: The part of the url contributed by the
            blueprint.  Generally speaking, BlueprintSetupState.url_prefix
        """
        parts = {'b': registration_prefix, 'a': self.prefix, 'e': url_part}
        return ''.join(parts[key] for key in self.url_part_order if parts[key])

    def _sanic_blueprint_register_hack(self, bp: Blueprint):
        def register(app, options):
            bp_obj = bp.old_register(app, options)
            self._init_app(bp)
            return bp_obj
        return register

    @staticmethod
    def _blueprint_setup_add_url_rule_patch(app,
                                            rule,
                                            endpoint=None,
                                            view_func=None,
                                            **options):
        """Method used to patch BlueprintSetupState.add_url_rule for setup
        state instance corresponding to this Api instance.  Exists primarily
        to enable _complete_url's function.

        :param blueprint_setup: The BlueprintSetupState instance (self)
        :param rule: A string or callable that takes a string and returns a
            string(_complete_url) that is the url rule for the endpoint
            being registered
        :param endpoint: See BlueprintSetupState.add_url_rule
        :param view_func: See BlueprintSetupState.add_url_rule
        :param **options: See BlueprintSetupState.add_url_rule
        """

        if callable(rule):
            rule = rule(app.url_prefix)
        elif app.url_prefix:
            rule = app.url_prefix + rule
        options.setdefault('subdomain', app.subdomain)
        if endpoint is None:
            endpoint = _endpoint_from_view_func(view_func)
        defaults = app.url_defaults
        if 'defaults' in options:
            defaults = dict(defaults, **options.pop('defaults'))
        app.add_url_rule(
            rule,
            '%s.%s' % (app.blueprint.name, endpoint),
            view_func,
            defaults=defaults,
            **options)

    def _deferred_blueprint_init(self, setup_state):
        """Synchronize prefix between blueprint/api and registration options,
        then perform initialization with setup_state.app
        :class:`flask.Flask` object. When a :class:`flask_restful.Api` object
        is initialized with a blueprint,
        this method is recorded on the blueprint to be run when the blueprint
        is later registered to a :class:`flask.Flask` object.
        This method also monkeypatches BlueprintSetupState.add_url_rule with
        _blueprint_setup_add_url_rule_patch.

        :param setup_state: The setup state object passed to deferred functions
            during blueprint registration
        :type setup_state: flask.blueprints.BlueprintSetupState

        """

        self.blueprint_setup = setup_state
        if setup_state.add_url_rule.__name__ !=\
           '_blueprint_setup_add_url_rule_patch':
            setup_state._original_add_url_rule = setup_state.add_url_rule
            setup_state.add_url_rule = MethodType(
                Api._blueprint_setup_add_url_rule_patch, setup_state)
        if not setup_state.first_registration:
            raise ValueError(
                'sanic-restful blueprints can only be registered once.')
        self._init_app(setup_state.app)

    def _init_app(self, app):
        """Perform initialization actions with the given :class:`flask.Flask`
        object.

        :param app: The sanic application object
        :type app: Sanic()
        """
        if len(self.resources) > 0:
            for resource, urls, kwargs in self.resources:
                self._register_view(app, resource, *urls, **kwargs)

    def owns_endpoint(self, endpoint):
        """Tests if an endpoint name (not path) belongs to this Api.  Takes
        in to account the Blueprint name part of the endpoint name.

        :param endpoint: The name of the endpoint being checked
        :return: bool
        """

        if self.blueprint:
            if endpoint.startswith(self.blueprint.name):
                endpoint = endpoint.split(self.blueprint.name + '.', 1)[-1]
            else:
                return False
        return endpoint in self.endpoints

    def exc_register(self, handler, errors, app=None, blueprint=None):
        if app:
            app.error_handler.add(Exception, handler)
        elif blueprint:
            blueprint.exception()(handler)
        else:
            pass

    def mediatypes_method(self):
        """Return a method that returns a list of mediatypes
        """
        return lambda resource_cls: self.mediatypes() + \
            [self.default_mediatype]

    def add_resource(self, resource, *urls, **kwargs):
        """Adds a resource to the api.

        :param resource: the class name of your resource
        :type resource: :class:`Resource`

        :param urls: one or more url routes to match for the resource, standard
                     flask routing rules apply.  Any url variables will be
                     passed to the resource method as args.
        :type urls: str

        :param endpoint: endpoint name
            (defaults to :meth:`Resource.__name__.lower`
            Can be used to reference this route in :class:`fields.Url` fields
        :type endpoint: str

        :param resource_class_args: args to be forwarded to the constructor of
            the resource.
        :type resource_class_args: tuple

        :param resource_class_kwargs: kwargs to be forwarded to the constructor
            of the resource.
        :type resource_class_kwargs: dict

        Additional keyword arguments not specified above will be passed as-is
        to :meth:`flask.Flask.add_url_rule`.

        Examples::

            api.add_resource(HelloWorld, '/', '/hello')
            api.add_resource(Foo, '/foo', endpoint="foo")
            api.add_resource(FooSpecial, '/special/foo', endpoint="foo")

        """
        if self.app is not None:
            self._register_view(self.app, resource, *urls, **kwargs)
        else:
            self.resources.append((resource, urls, kwargs))

    def resource(self, *urls, **kwargs):
        """Wraps a :class:`~flask_restful.Resource` class, adding it to the
        api. Parameters are the same as :meth:`~flask_restful.Api.add_resource`

        Example::

            app = Flask(__name__)
            api = restful.Api(app)

            @api.resource('/foo')
            class Foo(Resource):
                def get(self):
                    return 'Hello, World!'

        """

        def decorator(cls):
            self.add_resource(cls, *urls, **kwargs)
            return cls

        return decorator

    def _register_view(self, app, resource, *urls, **kwargs):
        endpoint = kwargs.pop('endpoint', None) or resource.__name__.lower()
        self.endpoints.add(endpoint)
        resource_class_args = kwargs.pop('resource_class_args', ())
        resource_class_kwargs = kwargs.pop('resource_class_kwargs', {})

        # NOTE: 'view_functions' is cleaned up
        # from Blueprint class in Flask 1.0
        if endpoint in getattr(app, 'view_functions', {}):
            previous_view_class = app.view_functions[endpoint].__dict__[
                'view_class']

            # if you override the endpoint with a different class,
            # avoid the collision by raising an exception
            if previous_view_class != resource:
                raise ValueError(
                    'This endpoint (%s) is already set to the class %s.' %
                    (endpoint, previous_view_class.__name__))

        resource.mediatypes = self.mediatypes_method()  # Hacky
        resource.endpoint = endpoint
        resource_func = self.output(
            resource.as_view(self, *resource_class_args,
                             **resource_class_kwargs))

        for decorator in self.decorators:
            resource_func = decorator(resource_func)

        for url in urls:
            # If this Api has a blueprint
            if self.blueprint:
                # And this Api has been setup
                if self.blueprint_setup:
                    # Set the rule to a string directly,
                    # as the blueprint is already
                    # set up.
                    self.blueprint_setup.add_url_rule(
                        url, view_func=resource_func, **kwargs)
                    continue
                else:
                    # Set the rule to a function that expects the blueprint
                    # prefix to construct the final url.
                    # Allows deferment of url finalization
                    # in the case that the associated Blueprint
                    # has not yet been registered to an application,
                    # so we can wait for the registration prefix
                    rule = partial(self._complete_url, url)
            else:
                # If we've got no Blueprint, just build a url with no prefix
                rule = self._complete_url(url, '')
            # Add the url to the application or blueprint
            app.add_route(uri=rule, handler=resource_func, **kwargs)

    def output(self, resource):
        """Wraps a resource (as a flask view function), for cases where the
        resource does not directly return a response object

        :param resource: The resource as a flask view function
        """
        @wraps(resource)
        async def wrapper(request, *args, **kwargs):
            resp = resource(request, *args, **kwargs)
            while asyncio.iscoroutine(resp):
                resp = await resp
            if isinstance(resp,
                          ResponseBase):  # There may be a better way to test
                return resp
            data, code, headers = unpack(resp)
            return self.make_response(request, data, code, headers=headers)

        return wrapper

    def url_for(self, resource, **values):
        """Generates a URL to the given resource.

        Works like :func:`sanic.url_for`."""
        endpoint = resource.endpoint
        if self.blueprint:
            endpoint = '{0}.{1}'.format(self.blueprint.name, endpoint)
        return self.app.url_for(endpoint, **values)

    def make_response(self, request, data, *args, **kwargs):
        """Looks up the representation transformer for the requested media
        type, invoking the transformer to create a response object. This
        defaults to default_mediatype if no transformer is found for the
        requested mediatype. If default_mediatype is None, a 406 Not
        Acceptable response will be sent as per RFC 2616 section 14.1

        :param data: Python object containing response data to be transformed
        """
        default_mediatype = kwargs.pop('fallback_mediatype',
                                       None) or self.default_mediatype
        mediatype = best_match_accept_mimetype(
            request,
            self.representations,
            default=default_mediatype,
        )
        if mediatype is None:
            raise NotAcceptable('Not Accetable')
        if mediatype in self.representations:
            resp = self.representations[mediatype](request.app, data, *args,
                                                   **kwargs)
            resp.headers['Content-Type'] = mediatype
            return resp
        elif mediatype == 'text/plain':
            resp = text(str(data), *args, **kwargs)
            resp.headers['Content-Type'] = 'text/plain'
            return resp
        else:
            raise ServerError(None)

    def mediatypes(self):
        """Returns a list of requested mediatypes sent in the Accept header"""
        return [
            h
            for h, q in sorted(
                request.accept_mimetypes,
                key=operator.itemgetter(1),
                reverse=True)
        ]

    def representation(self, mediatype):
        """Allows additional representation transformers to be declared for the
        api. Transformers are functions that must be decorated with this
        method, passing the mediatype the transformer represents. Three
        arguments are passed to the transformer:

        * The data to be represented in the response body
        * The http status code
        * A dictionary of headers

        The transformer should convert the data appropriately for the mediatype
        and return a Flask response object.

        Ex::

            @api.representation('application/xml')
            def xml(data, code, headers):
                resp = make_response(convert_data_to_xml(data), code)
                resp.headers.extend(headers)
                return resp
        """

        def wrapper(func):
            self.representations[mediatype] = func
            return func

        return wrapper

    def unauthorized(self, request, response):
        """ Given a response, change it to ask for credentials """

        if self.serve_challenge_on_401:
            realm = request.app.config.get("HTTP_BASIC_AUTH_REALM",
                                           "sanic-restful")
            challenge = u"{0} realm=\"{1}\"".format("Basic", realm)

            response.headers['WWW-Authenticate'] = challenge
        return response


class Resource(HTTPMethodView):
    """
    Represents an abstract RESTful resource. Concrete resources should
    extend from this class and expose methods for each supported HTTP
    method. If a resource is invoked with an unsupported HTTP method,
    the API will return a response with status 405 Method Not Allowed.
    Otherwise the appropriate method is called and passed all arguments
    from the url rule used when adding the resource to an Api instance. See
    :meth:`~flask_restful.Api.add_resource` for details.
    """
    representations = None
    method_decorators = {}

    def __init__(self, request, *args, **kwargs):
        self.request = request

    def dispatch_request(self, request, *args, **kwargs):
        # Taken from flask
        # noinspection PyUnresolvedReferences
        meth = getattr(self, request.method.lower(), None)
        if meth is None and request.method == 'HEAD':
            meth = getattr(self, 'get', None)
        assert meth is not None, 'Unimplemented method %r' % request.method

        if isinstance(self.method_decorators, Mapping):
            decorators = self.method_decorators.get(request.method.lower(), [])
        else:
            decorators = self.method_decorators

        for decorator in decorators:
            meth = decorator(meth)

        resp = meth(request, *args, **kwargs)

        if isinstance(resp, ResponseBase):  # There may be a better way to test
            return resp

        representations = self.representations or OrderedDict()

        # noinspection PyUnresolvedReferences
        mediatype = best_match_accept_mimetype(
            request, representations, default=None)
        if mediatype in representations:
            data, code, headers = unpack(resp)
            resp = representations[mediatype](data, code, headers)
            resp.headers['Content-Type'] = mediatype
            return resp

        return resp


def marshal(data, fields, envelope=None):
    """Takes raw data (in the form of a dict, list, object) and a dict of
    fields to output and filters the data based on those fields.

    :param data: the actual object(s) from which the fields are taken from
    :param fields: a dict of whose keys will make up the final serialized
                   response output
    :param envelope: optional key that will be used to envelop the serialized
                     response


    >>> from flask_restful import fields, marshal
    >>> data = { 'a': 100, 'b': 'foo' }
    >>> mfields = { 'a': fields.Raw }

    >>> marshal(data, mfields)
    OrderedDict([('a', 100)])

    >>> marshal(data, mfields, envelope='data')
    OrderedDict([('data', OrderedDict([('a', 100)]))])

    """

    def make(cls):
        if isinstance(cls, type):
            return cls()
        return cls

    if isinstance(data, (list, tuple)):
        return (OrderedDict([(envelope, [marshal(d, fields) for d in data])])
                if envelope else [marshal(d, fields) for d in data])

    items = ((k, marshal(data, v)
              if isinstance(v, dict) else make(v).output(k, data))
             for k, v in fields.items())
    return OrderedDict(
        [(envelope, OrderedDict(items))]) if envelope else OrderedDict(items)


class marshal_with(object):
    """A decorator that apply marshalling to the return values of your methods.

    >>> from flask_restful import fields, marshal_with
    >>> mfields = { 'a': fields.Raw }
    >>> @marshal_with(mfields)
    ... def get():
    ...     return { 'a': 100, 'b': 'foo' }
    ...
    ...
    >>> get()
    OrderedDict([('a', 100)])

    >>> @marshal_with(mfields, envelope='data')
    ... def get():
    ...     return { 'a': 100, 'b': 'foo' }
    ...
    ...
    >>> get()
    OrderedDict([('data', OrderedDict([('a', 100)]))])

    see :meth:`flask_restful.marshal`
    """

    def __init__(self, fields, envelope=None):
        """
        :param fields: a dict of whose keys will make up the final
                       serialized response output
        :param envelope: optional key that will be used to envelop the
                        serialized response
        """
        self.fields = fields
        self.envelope = envelope

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            _cls = args[0] if args else None
            if isinstance(_cls, Resource):
                pass
            resp = f(*args, **kwargs)
            if isinstance(resp, tuple):
                data, code, headers = unpack(resp)
                return marshal(data, self.fields, self.envelope), code, headers
            else:
                return marshal(resp, self.fields, self.envelope)

        return wrapper


class marshal_with_field(object):
    """
    A decorator that formats the return values of your methods
     with a single field.

    >>> from flask_restful import marshal_with_field, fields
    >>> @marshal_with_field(fields.List(fields.Integer))
    ... def get():
    ...     return ['1', 2, 3.0]
    ...
    >>> get()
    [1, 2, 3]

    see :meth:`flask_restful.marshal_with`
    """

    def __init__(self, field):
        """
        :param field: a single field with which to marshal the output.
        """
        if isinstance(field, type):
            self.field = field()
        else:
            self.field = field

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            resp = f(*args, **kwargs)
            if isinstance(resp, tuple):
                data, code, headers = unpack(resp)
                return self.field.format(data), code, headers
            return self.field.format(resp)

        return wrapper
