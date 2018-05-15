import logging

from satori.rtm.client import Client

from serpentarium.logging.LoggingFormatter import LoggingFormatter
from serpentarium.logging.RtmLoggingHandler import RtmLoggingHandler


class LoggingUtil:
    """
    A class to encapsulate loogers creation
    """
    handler: logging.Handler = None

    @classmethod
    def get_logger(cls, name: str):
        """
        Creates a logger
        :param name: logger name
        :return: logger
        """
        if cls.handler is None:
            return logging.getLogger(name)
        else:
            return LoggingUtil.get_rtm_logger(name)

    @classmethod
    def setup_logging(cls, client: Client, settings: dict, tags: dict) -> None:
        """
        Setup rtm logging
        :param rt client
        :param settings: logging settings
        :param tags: tags to enrich the message
        :return:
        """
        client: Client = client
        handler = RtmLoggingHandler(client, settings['rtm']['channel'])
        handler.setFormatter(LoggingFormatter(tags))
        cls.handler = handler

    @classmethod
    def get_rtm_logger(cls, name: str) -> logging.Logger:
        """
        Creates a logger with rtm handler
        :param name: logger name
        :return: logger
        """
        if cls.handler is None:
            raise ValueError("Setup logging before trying to get logger!")
        logger = logging.getLogger(name)
        logger.addHandler(cls.handler)
        return logger
