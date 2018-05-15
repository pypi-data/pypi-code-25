from serpentarium.monitoring.Metric import Metric


class HeartbeatMetric(Metric):

    def __init__(self, name: str) -> None:
        super().__init__(name, "heartbeat")

    def get_value(self):
        return 1
