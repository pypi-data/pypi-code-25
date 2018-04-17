# coding=utf-8
# cython: profile=True
# Filename: sys.pyx
# cython: embedsignature=True
# pylint: disable=C0103
"""
Some unsorted, frequently used logic.

"""
from __future__ import division, absolute_import, print_function

try:
    import resource  # linux/macos
except ImportError:
    import psutil    # windows

import sys
from contextlib import contextmanager

from .logger import logging

__author__ = "Tamas Gal"
__copyright__ = "Copyright 2016, Tamas Gal and the KM3NeT collaboration."
__credits__ = []
__license__ = "MIT"
__maintainer__ = "Tamas Gal and Moritz Lotze"
__email__ = "tgal@km3net.de"
__status__ = "Development"

log = logging.getLogger(__name__)  # pylint: disable=C0103


@contextmanager
def ignored(*exceptions):
    """Ignore-context for a given list of exceptions.

    Example:
        with ignored(AttributeError):
            foo.a = 1

    """
    try:
        yield
    except exceptions:
        pass


def peak_memory_usage():
    """Return peak memory usage in MB"""
    if sys.platform.startswith('win'):
        p = psutil.Process()
        return p.memory_info().peak_wset / 1024 / 1024

    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    factor_mb = 1 / 1024
    if sys.platform == 'darwin':
        factor_mb = 1 / (1024 * 1024)
    return mem * factor_mb
