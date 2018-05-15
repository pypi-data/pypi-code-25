from typing import List

from datadog import initialize, api

from serpentarium.monitoring import Metric
from serpentarium.monitoring.Monitor import Monitor


class DatadogMonitor(Monitor):
    """
    A monitor, which report to the Datadog
    """

    def __init__(self, settings: dict, tags: dict) -> None:
        self.tags = tags
        self.prefix = settings['prefix']

        initialize(**settings['datadog'])

    def drain(self, metrics: List[object]) -> None:
        """
        Makes an http call to push the data to the Datadog
        :param metrics:
        :return:
        """
        for m in metrics:
            metric: Metric = m
            api.Metric.send(
                metric=self.prefix + '.' + metric.aspect,
                points=metric.get_value(),
                host="python-bot",
                tags=self.tags
            )
