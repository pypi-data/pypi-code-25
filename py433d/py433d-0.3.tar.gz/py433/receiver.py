import logging
import time
from rpi_rf import RFDevice
from collections import defaultdict

class receiver:

    def __init__(self, pin=27, handler=lambda x: print(x)):
        self.rfdevice = RFDevice(pin)
        self.rfdevice.enable_rx()
        self.handler = handler

        self.threshold = 1000000
        self.timestamps = defaultdict(int)

    def run(self):
        self.running = True
        logging.debug("Receiver ready")
        rfdevice = self.rfdevice
        timestamp = None
        while self.running:
            if rfdevice.rx_code_timestamp != timestamp:
                timestamp = rfdevice.rx_code_timestamp
                code = rfdevice.rx_code

                if rfdevice.rx_code_timestamp > self.timestamps[code] + self.threshold:
                    self.timestamps[code] = rfdevice.rx_code_timestamp
                    logging.debug(
                        "Received RF code: " + str(code) +
                        " [pulselength " + str(rfdevice.rx_pulselength) +
                        ", protocol " + str(rfdevice.rx_proto) + "]"
                    )
                    self.handler(code)
            time.sleep(0.01)

    def stop(self):
        self.running = False
        self.rfdevice.cleanup()