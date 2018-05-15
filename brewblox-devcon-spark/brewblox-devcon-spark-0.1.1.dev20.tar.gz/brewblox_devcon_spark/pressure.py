"""
Demo implementation for reading pressure sensor values from serial
"""

from collections import namedtuple
from contextlib import suppress

from aiohttp import web
from brewblox_devcon_spark import communication
from brewblox_service import brewblox_logger, features

LOGGER = brewblox_logger(__name__)

Measurement = namedtuple('Measurement', [
    'sensor1_1s',
    'sensor1_30s',
    'sensor2_1s',
    'sensor2_30s',
    'voltage1_1s',
    'voltage1_30s',
    'voltage2_1s',
    'voltage2_30s'
])


def setup(app: web.Application):
    features.add(app, PressureSensor(app))


def get_sensor(app: web.Application) -> 'PressureSensor':
    return features.get(app, PressureSensor)


class PressureSensor(features.ServiceFeature):

    def __init__(self, app: web.Application):
        super().__init__(app)

        self._conduit: communication.SparkConduit = None
        self._latest: Measurement = Measurement(*([0]*8))

    @property
    def latest(self):
        return self._latest._asdict()

    async def start(self, app: web.Application):
        await self.close()
        self._conduit = communication.get_conduit(app)
        self._conduit.add_data_callback(self._process_values)

    async def close(self, *_):
        with suppress(AttributeError):
            self._conduit.remove_data_callback(self._process_values)

        self._conduit = None

    async def _process_values(self, conduit, msg: str):
        if 'debug' in msg.lower():
            LOGGER.info(msg)
            return

        received = Measurement(*[int(v) for v in msg.split(',')])

        LOGGER.info(received)
        self._latest = received
