from __future__ import absolute_import

from datetime import datetime
from sys import version_info

from fluent import sender


if version_info >= (3, 3):
    get_datetime_timestamp = datetime.timestamp
else:
    from time import mktime

    def get_datetime_timestamp(dt):
        return mktime(dt.utctimetuple()) + dt.microsecond / 1e6


class FluentLogSender:
    def __init__(self, tag, host='127.0.0.1', port=24224, **kwargs):
        kwargs.setdefault('nanosecond_precision', True)
        self._sender = sender.FluentSender(
            tag=tag,
            host=host, port=port,
            **kwargs
        )

    def __del__(self):
        self._sender.close()

    def send(self, event, data, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()
        if isinstance(timestamp, datetime):
            timestamp = get_datetime_timestamp(timestamp)
        self._sender.emit_with_time(
            label=event,
            data=data,
            timestamp=timestamp
        )
