from .request import AdharaRequest
from .response import AdharaResponse
from .restview import RestView


def get_request_class():
    return AdharaRequest


def get_response_class():
    return AdharaRequest


def get_rest_view_class():
    return RestView
