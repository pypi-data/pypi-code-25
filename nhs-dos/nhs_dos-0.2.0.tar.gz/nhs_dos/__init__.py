# -*- coding: utf-8 -*-

"""Top-level package for NHS DoS Client."""

__author__ = """Matt Stibbs"""
__email__ = 'matt@stibbsy.co.uk'
__version__ = '0.2.0'

from .users import User
from .cases import Case
from .soap_api import SoapApiClient
from .rest_api import RestApiClient
