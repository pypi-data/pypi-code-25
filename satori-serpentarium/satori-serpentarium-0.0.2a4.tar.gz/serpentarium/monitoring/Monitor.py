import abc
from typing import List


class Monitor:
    """
    An abstract class for the monitor.
    """

    def __init__(self):
        self._list = []

    def drain(self, metrics: List[object]) -> None:
        """
        Collects the metrics
        :param metrics: a list of metrics to record
        """
        self._list.extend(metrics)

    @abc.abstractmethod
    def push(self) -> None:
        """
        Pushes the metrics to the endpoint
        """
        pass
