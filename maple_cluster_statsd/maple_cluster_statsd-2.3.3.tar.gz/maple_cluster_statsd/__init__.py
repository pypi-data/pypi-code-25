# -*- coding: utf-8 -*-

__version__ = '2.3.3'

from .stat_reporter import StatReporter
from .stat_reader import StatReader
from . import constants


def create_gateway_reporter(cmd, statsd_client, statsd_name_converter=None):
    return StatReporter(
        cmd,
        statsd_client,
        constants.GATEWAY_GAUGE_STAT_LIST,
        constants.GATEWAY_INCR_STAT_LIST,
        statsd_name_converter
    )


def create_forwarder_reporter(cmd, statsd_client, statsd_name_converter=None):
    return StatReporter(
        cmd,
        statsd_client,
        constants.FORWARDER_GAUGE_STAT_LIST,
        constants.FORWARDER_INCR_STAT_LIST,
        statsd_name_converter
    )
