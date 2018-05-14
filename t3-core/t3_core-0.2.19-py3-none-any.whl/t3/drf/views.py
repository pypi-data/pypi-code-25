import sys
import traceback
import logging
from collections import OrderedDict
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from t3.util import get_response_type


log = logging.getLogger(__name__)


def enveloped_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    exc_info = sys.exc_info()
    response = exception_handler(exc, context)
    traceback_list = ''.join(traceback.format_exc()).split('\n')

    # Gather exception details, such as trace info
    exception_details = OrderedDict([
        ('exception_class', str(exc_info[0])),
        ('exception_message', str(exc_info[1])),
        ('exception_traceback', traceback_list),
    ])

    # Now add the HTTP status code to the response.
    if not response:
        response = Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Build response data
    response.data = OrderedDict([
        ('status', get_response_type(response.status_code)),
        ('code', response.status_code),
    ])

    # If debug mode is on, return exception details
    if settings.DEBUG:
        response.data['data'] = exception_details

        # If 500, log exception details
    if response.status_code == 500:
        log.error(OrderedDict([
            ('status', get_response_type(response.status_code)),
            ('code', response.status_code),
            ('data', dict(exception_details)),
        ]))

    # If debug is on, return trace info
    if settings.DEBUG:
        response.data['data'] = exception_details

    return response
