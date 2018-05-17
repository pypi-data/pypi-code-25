"""
Demo implementation for reading pressure sensor values from serial
"""

from collections import namedtuple
from contextlib import suppress
from datetime import datetime
from logging import FileHandler, Formatter
from typing import Iterator

import aiofiles
from aiohttp import web
from brewblox_devcon_spark import communication
from brewblox_service import brewblox_logger, features

LOGGER = brewblox_logger(__name__)

DENSITY = 0.9982
GRAVITY = 9.81

KEYS = [
    'sensor1_1s',
    'sensor1_30s',
    'sensor2_1s',
    'sensor2_30s',
    'voltage1_1s',
    'voltage1_30s',
    'voltage2_1s',
    'voltage2_30s'
]

Measurement = namedtuple('Measurement', KEYS)


def setup(app: web.Application):
    features.add(app, PressureSensor(app))


def get_sensor(app: web.Application) -> 'PressureSensor':
    return features.get(app, PressureSensor)


def calculate_values(raw,
                     voltage,
                     calibration_voltage,
                     voltage_sensitivity,
                     bits_per_mbar
                     ) -> dict:

    compensated = raw - (voltage - calibration_voltage) * voltage_sensitivity
    pressure = compensated / bits_per_mbar
    height = pressure / (DENSITY * GRAVITY)

    return dict(
        raw=raw,
        voltage=voltage,
        compensated=compensated,
        pressure=pressure,
        height=height
    )


class PressureSensor(features.ServiceFeature):

    def __init__(self, app: web.Application):
        super().__init__(app)

        self._conduit: communication.SparkConduit = None
        self._latest: dict = {}
        self._last_update: datetime = None

        self._csv_logger = brewblox_logger('raw_values')

        self._calibration_voltage = [None, None]
        self._voltage_sensitivity = [None, None]
        self._pressure_per_bit = None

    @property
    def latest(self):
        return self._last_update, self._latest

    async def start(self, app: web.Application):
        await self.close()
        self._conduit = communication.get_conduit(app)
        self._conduit.add_data_callback(self._process_values)

        config = app['config']
        self._calibration_voltage = config['calibration_voltage']
        self._voltage_sensitivity = config['voltage_sensitivity']
        self._pressure_per_bit = config['bits_per_mbar']

        handler = FileHandler(config['raw_data_file'])
        handler.setFormatter(Formatter('%(asctime)s.%(msecs)03d,%(message)s', '%Y/%m/%d-%H:%M:%S'))
        self._csv_logger.addHandler(handler)

    async def close(self, *_):
        with suppress(AttributeError):
            self._conduit.remove_data_callback(self._process_values)

        self._conduit = None

    async def _process_values(self, conduit, msg: str):
        if 'debug' in msg.lower():
            LOGGER.info(msg)
            return

        self._csv_logger.info(msg)

        received = Measurement(*[int(v) for v in msg.split(',')])

        self._last_update = datetime.now()
        self._latest = self._from_measurement(received)

    def _from_measurement(self, measurement: Measurement) -> dict:
        return {
            'lower_sensor': {
                'updated_1s': calculate_values(
                    measurement.sensor1_1s,
                    measurement.voltage1_1s,
                    self._calibration_voltage[0],
                    self._voltage_sensitivity[0],
                    self._pressure_per_bit
                ),
                'updated_30s': calculate_values(
                    measurement.sensor1_30s,
                    measurement.voltage1_30s,
                    self._calibration_voltage[0],
                    self._voltage_sensitivity[0],
                    self._pressure_per_bit
                )
            },
            'upper_sensor': {
                'updated_1s': calculate_values(
                    measurement.sensor2_1s,
                    measurement.voltage2_1s,
                    self._calibration_voltage[1],
                    self._voltage_sensitivity[1],
                    self._pressure_per_bit
                ),
                'updated_30s': calculate_values(
                    measurement.sensor2_30s,
                    measurement.voltage2_30s,
                    self._calibration_voltage[1],
                    self._voltage_sensitivity[1],
                    self._pressure_per_bit
                )
            }
        }

    async def recalculate(self, input_file: str) -> Iterator[dict]:
        async with aiofiles.open(input_file) as infile:
            while True:
                line = await infile.readline()
                if not line:
                    break

                vals = line.split(',')[1:]  # discard timestamp
                meas = Measurement(*[int(v) for v in vals])
                yield self._from_measurement(meas)
