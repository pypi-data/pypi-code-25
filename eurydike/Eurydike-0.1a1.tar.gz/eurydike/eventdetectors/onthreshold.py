from eurydike.eventdetectors.abstracteventdetector import AbstractEventDetector
from enum import Enum


class Comparator(Enum):
    GREATERTHAN = (lambda x,y : x > y),
    LOWERTHAN = (lambda x,y: x < y),
    EQUALTO = (lambda x,y: x == y),

    @classmethod
    def get_enum(cls, text, logger):
        if text.lower()=="greaterthan" or text.lower()=="gt" or text.lower()==">":
            return cls.GREATERTHAN
        elif text.lower()=="lowerthan" or text.lower()=="lt" or text.lower()=="<":
            return cls.LOWERTHAN
        elif text.lower()=="equalto" or text.lower()=="==":
            return cls.EQUALTO
        else:
            logger.error("Comperator.get_enum - unkown value '{}'.".format(text))
            raise ValueError("Comperator.get_enum - unkown value '{}'.".format(text))

    def __call__(self, *args, **kwargs):
        return self.value[0](*args, **kwargs)

class OnThreshold(AbstractEventDetector):
    _threshold = None
    _comparator = None

    def __init__(self, config, parent_logger, mqtt_client):
        AbstractEventDetector.__init__(self, config, parent_logger, mqtt_client)
        self._comparator = Comparator.get_enum(self._config["comparator"], self._logger)
        self._threshold = self._config["threshold"]

    def _is_violation(self, value):
        return self._comparator(value, self._threshold)


