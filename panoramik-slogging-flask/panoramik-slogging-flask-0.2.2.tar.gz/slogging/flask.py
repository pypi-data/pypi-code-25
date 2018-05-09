from __future__ import absolute_import

import logging
import time
import types
from functools import partial
from random import randrange

from flask import has_request_context, g as flask_g, request as flask_request
from flask.signals import request_started, request_tearing_down, request_finished
from six import wraps

from slogging import SLoggerHandler


def with_request_id(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        request_id = flask_g.get('slogger_request_id', None) if has_request_context() else None
        kwargs.setdefault('request_id', request_id)
        return func(*args, **kwargs)

    return decorated


class FlaskRequestSLoggerHandler(SLoggerHandler):
    def __init__(self, request_id_header=None, request_id_func=None, **kwargs):
        super(FlaskRequestSLoggerHandler, self).__init__(**kwargs)
        self.request_id_header = request_id_header
        self.request_id_func = request_id_func

    def install(self, app, **kwargs):
        """
        Installs this flask slogger to all Flask applications
        """
        super(FlaskRequestSLoggerHandler, self).install(**kwargs)

        request_started.connect(self.__before_request, sender=app)
        request_finished.connect(self.__after_request, sender=app)
        request_tearing_down.connect(self.__request_tearing_down, sender=app)
        app.handle_user_exception = types.MethodType(partial(
            self.__app_handle_user_exception,
            app.handle_user_exception
        ), app)

        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.WARNING)

    @with_request_id
    def _logline(self, *args, **kwargs):
        if 'severity_no' in kwargs and hasattr(flask_g, 'slogger_log_severity_no'):
            flask_g.slogger_log_severity_no = max(flask_g.slogger_log_severity_no, kwargs['severity_no'])
        super(FlaskRequestSLoggerHandler, self)._logline(*args, **kwargs)

    @with_request_id
    def _request_start(self, *args, **kwargs):
        super(FlaskRequestSLoggerHandler, self)._request_start(*args, **kwargs)

    @with_request_id
    def _request_finish(self, *args, **kwargs):
        if flask_g.slogger_log_severity_no > logging.NOTSET:
            kwargs.setdefault('log_severity', logging.getLevelName(flask_g.slogger_log_severity_no))
        super(FlaskRequestSLoggerHandler, self)._request_finish(*args, **kwargs)

    @with_request_id
    def set_request_custom(self, *args, **kwargs):
        super(FlaskRequestSLoggerHandler, self).set_request_custom(*args, **kwargs)

    def _generate_random_request_id(self):
        return '{}-{:x}#{:x}'.format(self.backend_name, int(time.time() * 1000), randrange(0xffffffff + 1))

    def __app_handle_user_exception(self, orig_handle, app, exc):
        exc_info = type(exc), exc, getattr(exc, '__traceback__', None)
        self._logline(
            message=None,
            severity='ERROR',
            exc_info=exc_info
        )
        return orig_handle(exc)

    def __before_request(self, sender):
        if self.request_id_func is not None:
            request_id = self.request_id_func()
        elif self.request_id_header is not None:
            request_id = flask_request.headers.get(self.request_id_header, None)
        else:
            request_id = None

        flask_g.slogger_request_id = request_id or self._generate_random_request_id()
        flask_g.slogger_log_severity_no = logging.NOTSET

        ip = flask_request.remote_addr
        url = flask_request.full_path.rstrip('?')
        method = flask_request.method
        host = flask_request.host

        self._request_start(
            ip=ip,
            url=url, method=method,
            host=host
        )

    def __after_request(self, sender, response):
        flask_g.slogger_response_status_code = response.status_code

    def __request_tearing_down(self, sender, exc):
        response_status_code = flask_g.get('slogger_response_status_code', 500)
        self._request_finish(status_code=response_status_code)
