import uuid
from abc import abstractmethod

from serpentarium.engine import ModContext
from serpentarium.monitoring.HeartbeatMetric import HeartbeatMetric
from serpentarium.monitoring.Monitor import Monitor


class Mod:
    """
    A minimal component of a bot.
    """

    def __init__(self, name: str, id: uuid, settings: dict, context: ModContext) -> None:
        """
        :param name: mod name
        :param id: mod id
        :param settings: mod settings
        :param context: execution context
        """
        self.context = context
        self.settings = settings
        self.id = id
        self.name = name
        self._stats = [HeartbeatMetric(name + "." + "heartbeat")]

    def on_stats(self, monitor: Monitor) -> None:
        """
        Drains the mod stats to the monitor
        :param monitor: monitor to drain to
        :return:
        """
        self.context.execute_blocking(monitor.drain, self._stats)

    @abstractmethod
    def on_stop(self) -> None:
        """
        Performs the shutdown logic
        :return:
        """
        pass

    @abstractmethod
    def on_start(self) -> None:
        """
        Performs the startup logic
        :return:
        """
        pass

    @abstractmethod
    async def on_message(self, message: dict) -> None:
        """
        Processes the message
        :param message:
        :return:
        """
        pass

    def emit(self, message: dict) -> None:
        """
        Passes the message downstream
        :param message: message to pass
        :return:
        """
        self.context.emit(self.id, message)
