from paho.mqtt.client import Client
import logging

class mqtt:

    def __init__(self, host="localhost", port=1883, username=None, password=None, codes=dict()):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.codes = codes
        logging.debug("Loaded codes mapping: '" + str(self.codes) + "'")

    @property
    def client(self):
        client = Client()
        if self.username and self.password:
            client.username_pw_set(self.username, password=self.password)
        client.connect(self.host, self.port, 60)
        return client

    def post(self, code):
        topic, content = self.topic_content(code)
        if topic and content:
            logging.debug("Publishing '" + content + "' to '" + topic + "'")
            self.client.publish(topic, content)

    def topic_content(self, code):
        d = self.codes.get(str(code), dict())
        return d.get("topic", None), d.get("content", None)