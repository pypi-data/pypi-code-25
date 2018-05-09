from __future__ import print_function

import sys
from datetime import datetime


if sys.version_info >= (3, 3):
    get_datetime_timestamp = datetime.timestamp
else:
    from time import mktime

    def get_datetime_timestamp(dt):
        return mktime(dt.utctimetuple()) + dt.microsecond / 1e6


class DebugLogSender:
    def __init__(self, fp=sys.stderr):
        self.fp = fp

    def send(self, event, data, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()
        if isinstance(timestamp, datetime):
            timestamp = get_datetime_timestamp(timestamp)
        print('[{:.3f}] {}: {}'.format(timestamp, event, data), file=self.fp)
