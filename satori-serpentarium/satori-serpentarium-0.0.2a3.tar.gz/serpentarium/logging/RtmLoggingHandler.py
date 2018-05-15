from logging import Handler, LogRecord

from satori.rtm.client import Client


class RtmLoggingHandler(Handler):
    """
    Logging handler, which writes logs to an rtm channel
    """

    def __init__(self, client: Client, channel: str) -> None:
        super().__init__()
        self.client = client
        self.channel = channel

    def emit(self, record: LogRecord) -> None:
        """
        Writes message to the rtm
        :param record: logging record
        :return:
        """
        self.client.publish(self.channel, self.formatter.format(record))
