import logging


class AbstractEventDetector:
    _config = None
    _logger = None
    _name = None
    _mqtt_client = None
    _event_active = None
    _topic_sub = None
    _topic_pub = None
    _responses = None

    def __init__(self, config, parent_logger, mqtt_client):
        self._config = config
        self._logger = parent_logger.getChild(__name__)
        self._logger.info("{}.__init__ - initializing".format(self.__class__.__name__))
        self._logger.debug("{}.__init__ - configuration: {}".format(self.__class__.__name__, self._config))

        self._name = self._config["name"]

        self._mqtt_client = mqtt_client
        self._topic_pub = self._config["topic-pub"]
        self._topic_sub = self._config["topic-sub"]
        self._responses = {}
        for k, v in self._config["responses"].items():
            if v is None or v == "":
                continue
            self._responses[k] = v

        self._event_active = False

    def _message_handler(self, value):
        try:
            value = int(value)
        except ValueError:
            value = float(value)

        if self._is_violation(value):
            # threshold is violated
            if not self._event_active:
                self._logger.info("{}._message_handler ({}) - threshold violation detected (value: {}).".
                                  format(self.__class__.__name__, self._name, value))
                try:
                    self._mqtt_client.publish(self._topic_pub, self._responses["on-violation"])
                except KeyError:
                    pass
            self._event_active = True
        else:
            if self._event_active:
                self._logger.info("{}._message_handler ({}) - threshold restored (value: {}).".
                                  format(self.__class__.__name__, self._name, value, ))
                try:
                    self._mqtt_client.publish(self._topic_pub, self._responses["on-restoration"])
                except KeyError:
                    pass
            self._event_active = False

    def _is_violation(self, value):
        raise NotImplementedError

    def start(self):
        self._mqtt_client.subscribe(self._topic_sub, self._message_handler)

    def stop(self):
        self._mqtt_client.unsubscribe(self._topic_sub, self._message_handler)
