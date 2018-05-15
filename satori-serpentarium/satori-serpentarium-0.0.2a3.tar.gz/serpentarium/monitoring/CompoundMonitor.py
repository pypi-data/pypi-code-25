from typing import List

from serpentarium.monitoring.Monitor import Monitor


class CompoundMonitor(Monitor):
    """
    A combination of monitors
    """

    def __init__(self, monitors: List[Monitor]):
        self.monitors = monitors

    def drain(self, metrics: List[object]) -> None:
        """
        Drains metrics to multiple monitors
        :param metrics: metrics to drain
        :return:
        """
        for monitor in self.monitors:
            monitor.drain(metrics)
