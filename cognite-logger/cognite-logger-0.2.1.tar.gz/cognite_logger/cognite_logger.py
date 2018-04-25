import logging
import threading
import time
import os
from inspect import getframeinfo, stack
from typing import Dict

from pythonjsonlogger import jsonlogger

class CustomFormatter(logging.Formatter):

    def format(self, record):
        record.caller_file = os.path.basename(record.sourceLocation["file"])
        record.caller_line = record.sourceLocation["line"]
        return super(CustomFormatter, self).format(record)

def configure_logger(logger_name: str, log_level: str, log_json: bool):
    """
    Configure logger
    :param logger_name: Name of the logger
    :param log_json: bool Flag for logging json or not
    :param log_level: Log level. E.g. "DEBUG"
    :return: Logger
    """
    logger = logging.getLogger(logger_name)
    if not logger.hasHandlers():
        log_handler = logging.StreamHandler()
        if log_json:
            formatter = jsonlogger.JsonFormatter()
            log_handler.setFormatter(formatter)
        else:
            formatter = CustomFormatter(
                "%(asctime)s.%(msecs)03d [%(levelname)-8s] %(threadName)s. %(message)s (%(caller_file)s:%(caller_line)s)",
                "%Y-%m-%d %H:%M:%S",
            )
            log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)
        logger.setLevel(log_level)

    return logger


class CogniteLogger:
    """
    Class to manage logging. Default log_level is set to INFO.
    """
    def __init__(self, logger_name: str, log_level: str = "INFO", log_json: bool = True):
        # Setup logger
        self.logger = configure_logger(logger_name, log_level, log_json)

    def add_standard_fields(self, extra: Dict = {}):
        extra["timestamp"] = int(time.time())

        # Get information about who called the logger, so that we can add information about which filename, line number,
        # and function led to the log statement.
        caller = getframeinfo(stack()[2][0])
        source_location = {
            "file": str(caller.filename),
            "function": str(caller.function),
            "line": str(caller.lineno),
            "logger name": self.logger.name,
            "thread name": threading.current_thread().getName()
        }
        extra["sourceLocation"] = source_location

        return extra

    def debug(self, msg, extra: Dict = {}):
        extra["severity"] = "DEBUG"
        extra = self.add_standard_fields(extra)
        self.logger.debug(msg, extra=extra)

    def info(self, msg, extra: Dict = {}, exc_info=None):
        extra["severity"] = "INFO"
        extra = self.add_standard_fields(extra)
        self.logger.info(msg, extra=extra, exc_info=exc_info)

    def warning(self, msg, extra: Dict = {}, exc_info=None):
        extra["severity"] = "WARNING"
        extra = self.add_standard_fields(extra)
        self.logger.warning(msg, extra=extra, exc_info=exc_info)

    def error(self, msg, extra: Dict = {}, exc_info=None):
        extra["severity"] = "ERROR"
        extra = self.add_standard_fields(extra)
        self.logger.error(msg, extra=extra, exc_info=exc_info)

