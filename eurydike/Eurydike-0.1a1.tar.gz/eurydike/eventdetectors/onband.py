from eurydike.eventdetectors.abstracteventdetector import AbstractEventDetector


class OnBand(AbstractEventDetector):
    _upper_threshold = None
    _lower_threshold = None

    def __init__(self, config, parent_logger, mqtt_client):
        AbstractEventDetector.__init__(self, config, parent_logger, mqtt_client)
        self._upper_threshold = self._config["upper-threshold"]
        self._lower_threshold = self._config["lower-threshold"]
        if self._lower_threshold >= self._upper_threshold:
            self._logger.error("OnBand.__init__ ({}) - lower limit ({}) must be smaller than upper limit({}).".
                               format(self._name, self._lower_threshold, self._upper_threshold))
            raise ValueError("OnBand.__init__ ({}) - lower limit ({}) must be smaller than upper limit({}).".
                               format(self._name, self._lower_threshold, self._upper_threshold))

    def _is_violation(self, value):
        return not (self._lower_threshold <= value <= self._upper_threshold)
