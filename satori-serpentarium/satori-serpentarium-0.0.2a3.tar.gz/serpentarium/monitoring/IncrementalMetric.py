from serpentarium.monitoring.Metric import Metric


class IncrementalMetric(Metric):
    """
    A metric with an incremental integer value
    """

    def __init__(self, name: str) -> None:
        super().__init__(name, "sum")
        self.sum = 0

    def inc(self) -> None:
        """
        Increment value
        :return:
        """
        self.sum += 1

    def get_value(self):
        """
        Get current value
        :return:
        """
        return self.sum
