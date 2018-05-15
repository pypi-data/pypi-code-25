from serpentarium.monitoring.Metric import Metric


class AvgMetric(Metric):
    """
    A metric with an average value
    """

    def __init__(self, name: str) -> None:
        super().__init__(name, "avg")
        self.samples = 0
        self.avg = 0

    def sample(self, sample: int) -> None:
        """
        Add sample
        :return:
        """
        self.samples += 1
        self.avg = self.avg - self.avg / self.samples
        self.avg = self.avg + sample / self.samples

    def get_value(self):
        """
        Get current avg
        :return:
        """
        return self.avg
