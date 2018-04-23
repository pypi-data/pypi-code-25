# -*- coding: utf-8 -*-
from .__version import __version__
from .snitcher import Scoop, Snitcher
import logging

__author__ = 'Horacio Hoyos Rodriguez'
__copyright__ = 'Copyright , Kinori Technologies'

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())