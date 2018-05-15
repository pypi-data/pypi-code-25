import uuid

from satori.rtm.client import SubscriptionMode

from serpentarium.engine.Mod import Mod
from serpentarium.engine.ModContext import ModContext
from serpentarium.logging.LoggingUtil import LoggingUtil
from serpentarium.monitoring.IncrementalMetric import IncrementalMetric
from serpentarium.monitoring.Monitor import Monitor
from serpentarium.rtm.RtmClientUtil import RtmClientUtil


class RtmSubscriber(Mod):
    """
    Subscribes to an RTM channel and passes the messages further
    """

    def __init__(self, name: str, id: uuid, settings: dict, context: ModContext) -> None:
        super().__init__(name, id, settings, context)
        self.log = LoggingUtil.get_logger(self.__class__.__name__)
        self.rcv = IncrementalMetric(name + "." + "received")
        self._stats.append(self.rcv)
        self._client = RtmClientUtil.get_client(settings['rtm'])
        self.channel = settings['rtm']['channel']
        self.log.info("Created an instance of RtmSubscriber mod")

    def on_stop(self):
        self.log.info("RtmSubscriber for channel {} is stopped".format(self.channel))
        pass

    def on_start(self):
        """
        Subscribes to an rtm channel
        :return:
        """
        self._client.subscribe(channel_or_subscription_id=self.channel,
                               subscription_observer=SubscriptionObserver(self),
                               mode=SubscriptionMode.RELIABLE)
        self.log.info("RtmSubscriber for channel {} started".format(self.channel))
        pass

    async def on_message(self, message: dict):
        pass


class SubscriptionObserver(object):
    """
    Reacts on RTM subscription data
    """

    def __init__(self, mod: RtmSubscriber):
        self.mod = mod

    def on_subscription_data(self, data):
        """
        Passes the message downstream
        :param data:
        :return:
        """
        for message in data['messages']:
            self.mod.log.debug('Got message {0}'.format(message))
            self.mod.emit(message)
            self.mod.rcv.inc()

    def on_enter_subscribed(self):
        self.mod.log.info('Subscription to the channel {} is now active'.format(self.mod.channel))
