import abc
from typing import List


class Monitor:
    """
    An abstract class for the monitor.
    """

    @abc.abstractmethod
    def drain(self, metrics: List[object]) -> None:
        """
        Records the mtrics provided
        :param metrics: a list of metrics to record
        """
        pass
