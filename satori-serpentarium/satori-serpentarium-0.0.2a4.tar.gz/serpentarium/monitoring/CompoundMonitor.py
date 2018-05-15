from typing import List

from serpentarium.monitoring.Monitor import Monitor


class CompoundMonitor(Monitor):
    """
    A combination of monitors
    """

    def __init__(self, monitors: List[Monitor]):
        super().__init__()
        self.monitors = monitors

    def drain(self, metrics: List[object]) -> None:
        for monitor in self.monitors:
            monitor.drain(metrics)

    def push(self) -> None:
        for monitor in self.monitors:
            monitor.push()
