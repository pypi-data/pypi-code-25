# Copyright 2015 Florian Ludwig
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from __future__ import absolute_import, division, print_function, with_statement


import tornado.web
import tornado.httpserver
import tornado.httputil
import tornado.ioloop
from tornado import gen
from tornado import iostream
from tornado.web import HTTPError
from tornado.concurrent import is_future
from tornado.web import _has_stream_request_body

import rw.cfg
import rw.scope
import rw.routing
import rw.template
import rw.server
import rw.event


PRE_REQUEST = rw.event.Event('httpbase.pre_request')
POST_REQUEST = rw.event.Event('httpbase.post_request')


class Application(ReversibleRouter):
    def __init__(self, handlers=None, default_host=None, transforms=None,
                 **settings):
        if transforms is None:
            self.transforms = []
            if settings.get("compress_response") or settings.get("gzip"):
                self.transforms.append(GZipContentEncoding)
        else:
            self.transforms = transforms
        self.default_host = default_host
        self.settings = settings
        self.ui_modules = {'linkify': _linkify,
                           'xsrf_form_html': _xsrf_form_html,
                           'Template': TemplateModule,
                           }
        self.ui_methods = {}
        self._load_ui_modules(settings.get("ui_modules", {}))
        self._load_ui_methods(settings.get("ui_methods", {}))
        if self.settings.get("static_path"):
            path = self.settings["static_path"]
            handlers = list(handlers or [])
            static_url_prefix = settings.get("static_url_prefix",
                                             "/static/")
            static_handler_class = settings.get("static_handler_class",
                                                StaticFileHandler)
            static_handler_args = settings.get("static_handler_args", {})
            static_handler_args['path'] = path
            for pattern in [re.escape(static_url_prefix) + r"(.*)",
                            r"/(favicon\.ico)", r"/(robots\.txt)"]:
                handlers.insert(0, (pattern, static_handler_class,
                                    static_handler_args))

        if self.settings.get('debug'):
            self.settings.setdefault('autoreload', True)
            self.settings.setdefault('compiled_template_cache', False)
            self.settings.setdefault('static_hash_cache', False)
            self.settings.setdefault('serve_traceback', True)

        self.wildcard_router = _ApplicationRouter(self, handlers)
        self.default_router = _ApplicationRouter(self, [
            Rule(AnyMatches(), self.wildcard_router)
        ])

        # Automatically reload modified modules
        if self.settings.get('autoreload'):
            from tornado import autoreload
            autoreload.start()

    def listen(self, port, address="", **kwargs):
        """Starts an HTTP server for this application on the given port.

        This is a convenience alias for creating an `.HTTPServer`
        object and calling its listen method.  Keyword arguments not
        supported by `HTTPServer.listen <.TCPServer.listen>` are passed to the
        `.HTTPServer` constructor.  For advanced uses
        (e.g. multi-process mode), do not use this method; create an
        `.HTTPServer` and call its
        `.TCPServer.bind`/`.TCPServer.start` methods directly.

        Note that after calling this method you still need to call
        ``IOLoop.current().start()`` to start the server.

        Returns the `.HTTPServer` object.

        .. versionchanged:: 4.3
           Now returns the `.HTTPServer` object.
        """
        # import is here rather than top level because HTTPServer
        # is not importable on appengine
        from tornado.httpserver import HTTPServer
        server = HTTPServer(self, **kwargs)
        server.listen(port, address)
        return server

    def add_handlers(self, host_pattern, host_handlers):
        """Appends the given handlers to our handler list.

        Host patterns are processed sequentially in the order they were
        added. All matching patterns will be considered.
        """
        host_matcher = HostMatches(host_pattern)
        rule = Rule(host_matcher, _ApplicationRouter(self, host_handlers))

        self.default_router.rules.insert(-1, rule)

        if self.default_host is not None:
            self.wildcard_router.add_rules([(
                DefaultHostMatches(self, host_matcher.host_pattern),
                host_handlers
            )])

    def add_transform(self, transform_class):
        self.transforms.append(transform_class)

    def find_handler(self, request, **kwargs):
        route = self.default_router.find_handler(request)
        if route is not None:
            return route

        if self.settings.get('default_handler_class'):
            return self.get_handler_delegate(
                request,
                self.settings['default_handler_class'],
                self.settings.get('default_handler_args', {}))

        return self.get_handler_delegate(
            request, ErrorHandler, {'status_code': 404})

    def get_handler_delegate(self, request, target_class, target_kwargs=None,
                             path_args=None, path_kwargs=None):
        """Returns `~.httputil.HTTPMessageDelegate` that can serve a request
        for application and `RequestHandler` subclass.

        :arg httputil.HTTPServerRequest request: current HTTP request.
        :arg RequestHandler target_class: a `RequestHandler` class.
        :arg dict target_kwargs: keyword arguments for ``target_class`` constructor.
        :arg list path_args: positional arguments for ``target_class`` HTTP method that
            will be executed while handling a request (``get``, ``post`` or any other).
        :arg dict path_kwargs: keyword arguments for ``target_class`` HTTP method.
        """
        return _HandlerDelegate(
            self, request, target_class, target_kwargs, path_args, path_kwargs)

    def reverse_url(self, name, *args):
        """Returns a URL path for handler named ``name``

        The handler must be added to the application as a named `URLSpec`.

        Args will be substituted for capturing groups in the `URLSpec` regex.
        They will be converted to strings if necessary, encoded as utf8,
        and url-escaped.
        """
        reversed_url = self.default_router.reverse_url(name, *args)
        if reversed_url is not None:
            return reversed_url

        raise KeyError("%s not found in named urls" % name)

    def log_request(self, handler):
        """Writes a completed HTTP request to the logs.

        By default writes to the python root logger.  To change
        this behavior either subclass Application and override this method,
        or pass a function in the application settings dictionary as
        ``log_function``.
        """
        if "log_function" in self.settings:
            self.settings["log_function"](handler)
            return
        if handler.get_status() < 400:
            log_method = access_log.info
        elif handler.get_status() < 500:
            log_method = access_log.warning
        else:
            log_method = access_log.error
        request_time = 1000.0 * handler.request.request_time()
        log_method("%d %s %.2fms", handler.get_status(),
                   handler._request_summary(), request_time)
