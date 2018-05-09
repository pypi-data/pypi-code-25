from urllib.parse import urlparse

from flask import request, abort


__version_info__ = ('0', '0', '1')
__version__ = '.'.join(__version_info__)
__author__ = 'Skyler Berg'
__license__ = 'APACHE 2.0'
__copyright__ = '(c) 2018 by Skyler Berg'
__all__ = ['AntiCsrf']

SAFE_METHODS = set(['GET', 'HEAD', 'OPTIONS', 'TRACE'])

# Error messages
NO_ORIGIN_AND_REFERER = 'Request is missing "origin" and "referer" headers'
NO_HOST = 'Request is missing host header'
HOST_ORIGIN_MISMATCH = 'Request host did not match request origin'


class CrossOriginRequestError(Exception):
    pass


class AntiCsrf(object):
    def __init__(self, app):
        self.app = app
        self._error_handler = lambda exception: abort(403)

        @app.before_request
        def prevent_csrf():
            if request.method in SAFE_METHODS:
                return
            origin = None
            host = None
            if 'origin' in request.headers:
                origin = request.headers['origin'].lower()
            elif 'referer' in request.headers:
                origin = request.headers['referer'].lower()

            if origin is None:
                raise CrossOriginRequestError(NO_ORIGIN_AND_REFERER)

            if 'host' in request.headers:
                host = request.headers['host'].lower()

            if host is None:
                raise CrossOriginRequestError(NO_HOST)

            parsed_origin = urlparse(origin)
            if host != parsed_origin.netloc:
                raise CrossOriginRequestError(HOST_ORIGIN_MISMATCH)

        @app.errorhandler(CrossOriginRequestError)
        def call_error_handler(exception):
            return self._error_handler(exception)

    def set_error_handler(self, error_handler):
        self._error_handler = error_handler
