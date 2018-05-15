import abc


class Metric:
    """
    An abstract metric
    """

    def __init__(self, name: str, _type: str) -> None:
        self.type = _type
        self.aspect: str = name

    @abc.abstractmethod
    def get_value(self):
        """
        Get the metric value
        :return:
        """
        pass
