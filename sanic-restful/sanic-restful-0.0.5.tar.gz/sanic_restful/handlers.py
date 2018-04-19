import sys

from sanic.log import error_logger
from sanic.exceptions import SanicException
from werkzeug.datastructures import Headers

from sanic_restful.utils import http_status_message


class RestfulErrorHandle:

    def __init__(self,
                 errors,
                 make_response,
                 unauthorized,
                 representations,
                 default_mediatype='application/json'):
        self.errors = errors or dict()
        self.make_response = make_response
        self.unauthorized = unauthorized
        self.representations = representations
        self.default_mediatype = default_mediatype

    def handler(self, request, exc):
        headers = Headers()

        if isinstance(exc, SanicException):
            status_code = exc.status_code
            args = getattr(exc, 'args', None)
            if args:
                message = args[0]
            else:
                message = http_status_message(status_code)
            default_data = {'message': message}
            headers = getattr(exc, 'headers', headers)
        else:
            status_code = 500
            default_data = {
                'message': http_status_message(status_code)
            }

        data = getattr(exc, 'data', default_data)

        if status_code and status_code >= 500:
            exc_info = sys.exc_info()
            if exc_info[1] is None:
                exc_info = None
            error_logger.exception(exc_info)

        error_cls_name = type(exc).__name__
        if error_cls_name in self.errors:
            custom_data = self.errors.get(error_cls_name, {})
            status_code = custom_data.get('status', 500)
            data.update(custom_data)

        if status_code == 406 and self.default_mediatype is None:
            supported_mediatypes = list(self.representations.keys())
            fallback_mediatype = supported_mediatypes[
                0] if supported_mediatypes else 'text/plain'
            resp = self.make_response(
                request,
                data,
                status_code,
                headers,
                fallback_mediatype=fallback_mediatype)
        else:
            resp = self.make_response(request, data, status_code, headers)

        if status_code == 401:
            resp = self.unauthorized(request, resp)
        return resp

    def __call__(self, request, exception):
        return self.handler(request, exception)
