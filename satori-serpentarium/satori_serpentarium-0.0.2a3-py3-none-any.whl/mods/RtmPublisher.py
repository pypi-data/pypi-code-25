import uuid

from serpentarium.engine.Mod import Mod
from serpentarium.engine.ModContext import ModContext
from serpentarium.logging.LoggingUtil import LoggingUtil
from serpentarium.monitoring.IncrementalMetric import IncrementalMetric
from serpentarium.rtm.RtmClientUtil import RtmClientUtil


class RtmPublisher(Mod):
    """
    Publishes messages to an RTM channel
    """

    def __init__(self, name: str, id: uuid, settings: dict, context: ModContext) -> None:
        super().__init__(name, id, settings, context)

        self._log = LoggingUtil.get_logger(self.__class__.__name__)
        self.sent = IncrementalMetric(name + "." + "sent")
        self._stats.append(self.sent)
        self._client = RtmClientUtil.get_client(settings['rtm'])
        self._channel = settings['rtm']['channel']
        self._log.info("Created an instance of RtmPublisher mod")

    def on_stop(self):
        self._log.info("RtmPublisher for channel {} is stopped".format(self._channel))
        pass

    def on_start(self):
        self._log.info("RtmPublisher for channel {} started".format(self._channel))
        pass

    async def on_message(self, message: dict):
        """
        Sentds message to an rtm channel
        :param message: message to send
        :return:
        """
        self._client.publish(channel=self._channel, message=message)
        self.sent.inc()
