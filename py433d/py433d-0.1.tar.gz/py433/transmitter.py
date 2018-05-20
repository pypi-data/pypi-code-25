import logging
from signal import (
    signal,
    SIGINT
)
from time import sleep
from typing import List

from rpi_rf import RFDevice


class transmitter:

    def __init__(self, queue, messages=dict(), pin=17, protocol=1, pulse=180):
        signal(SIGINT, self.exithandler)
        self.rfdevice = RFDevice(pin)
        self.rfdevice.enable_tx()
        self.protocol = protocol
        self.pulse = pulse
        self.queue = queue
        self.messages = messages
        logging.debug("Loaded messages mapping: '" + str(self.messages) + "'")

    def run(self):
        logging.debug("Transmitter ready")
        self.consume()

    def consume(self):
        while True:
            message = self.queue.get()
            code, repeat = self.code(message.split())
            if code:
                for i in range(repeat):
                    # self.rfdevice.tx_code(1398531, self.protocol, self.pulse)
                    logging.debug("Transmitting '" + str(code) + "'")
                    sleep(0.01)
            else:
                logging.warning("Unrecognized message '" + message + "'")

    def code(self, message: List[str]):
        return self.code_for_message(message, self.messages)

    def code_for_message(self, message: List[str], mapping):
        code = 0
        repeat = 0

        if len(message) > 1:
            return self.code_for_message(message[1:], mapping.get(message[0], {}))
        else:
            item = mapping.get(message[0])
            if isinstance(item, int):
                code = item
                repeat = 1
            elif isinstance(item, dict):
                code = item.get("code")
                repeat = item.get("repeat", 1)
            return code, repeat


    def exithandler(self, signal, frame):
        self.rfdevice.cleanup()
