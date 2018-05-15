import json
import time
from logging import Formatter, LogRecord


class LoggingFormatter(Formatter):
    """
    Logging formatter to match the existing Java bots format
    """

    def __init__(self, tags: dict):
        super(LoggingFormatter, self).__init__()
        self.tags = tags

    def format(self, record: LogRecord) -> json:
        """
        Formats the message to match existing format
        :param record: log record
        :return: formatted json
        """
        data = {'threadName': record.threadName, 'level': record.levelname,
                'message': record.msg,
                'timestamp': int(round(time.time() * 1000)),
                'tags': self.tags}

        return json.dumps(data)
