from pelops.abstractmicroservice import AbstractMicroservice
from eurydike.eventdetectors.eventdetectorfactory import EventDetectorFactory


class EventDetectionManager(AbstractMicroservice):
    _event_detectors = None

    def __init__(self, config, mqtt_client=None, logger=None):
        AbstractMicroservice.__init__(self, config, "eventdetectors", mqtt_client=mqtt_client, logger=logger)
        self._event_detectors = EventDetectorFactory.create_elements(self._config, self._logger, self._mqtt_client)

    def _start(self):
        for event in self._event_detectors:
            event.start()

    def _stop(self):
        for event in self._event_detectors:
            event.stop()
