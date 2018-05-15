from satori.rtm.client import Client

from serpentarium.monitoring.Monitor import Monitor
from serpentarium.rtm.RtmClientUtil import RtmClientUtil


class RtmMonitor(Monitor):
    """
    A monitor, which send metrics to an RTM channel
    """

    def __init__(self, settings: dict, tags: dict) -> None:
        super().__init__()
        self.client: Client = RtmClientUtil.get_client(settings['rtm'])
        self.channel = settings['rtm']['channel']
        self.tags = tags
        self.prefix = settings['prefix']

    def push(self) -> None:
        """
        Sends metrics to the rtm
        :param metrics: metrics array
        :return:
        """
        self.client.publish(self.channel,
                            {'prefix': self.prefix, 'tags': self.tags,
                             'metrics': list(map(lambda x: vars(x), self._list))})
        self._list.clear()
