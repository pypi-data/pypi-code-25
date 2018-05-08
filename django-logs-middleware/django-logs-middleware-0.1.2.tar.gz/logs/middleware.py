"""
    ==============
    LOG MIDDLEWARE
    ==============
"""
import json
import sys
import traceback

from django.http import JsonResponse

from logs.app import Log

logger = Log()


class LogResourceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.body  # This is for avoid the RawPostDataException for CSRF Middleware
        response = self.get_response(request)
        if self.check_response(response):
            exception_ms = json.loads(response.content.decode('utf-8'))
            logger.exception_rsc(request=request, exception_ms=exception_ms, response=response)
        else:
            logger.info_rsc(request=request, response=response)
        return response

    @staticmethod
    def log_exception(exception):
        data = type_ = error_status = None

        if isinstance(exception, Exception):
            type_e, value, tb = sys.exc_info()
            type_ = str(type(exception).__name__)
            temp = traceback.format_exception(type_e, value, tb)
            data = []
            for i in temp:
                i.replace('"', "´")
                data.append(" ".join(i.replace('"', "´").split()))

            error_status = 500

        return type_, data, error_status

    @staticmethod
    def check_response(response):
        if type(response) is JsonResponse:
            body = json.loads(response.content.decode('utf-8'))
            if 'exception' in body:
                return True
        return False
