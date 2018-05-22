"""
Demo implementation for reading pressure sensor values from serial
"""

from collections import namedtuple
from contextlib import suppress
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
    'sensor_id',
    'value_1s',
    'value_30s',
    'voltage_1s',
    'voltage_30s',
    'unfiltered',
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
        self._csv_logger = brewblox_logger('raw_values')

        self._current: dict = {}
        self._latest: dict = None
        self._calibration_voltage = [None, None]
        self._voltage_sensitivity = [None, None]
        self._names = ['lower_sensor', 'upper_sensor']
        self._pressure_per_bit = None

    @property
    def latest(self):
        val = self._latest
        self._latest = None
        return val

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

        received = Measurement(*[int(v) for v in msg.split(',')])

        self._csv_logger.info(msg)
        self._current.update(self._from_measurement(received))
        self._latest = self._current

    def _from_measurement(self, measurement: Measurement) -> dict:
        idx = measurement.sensor_id

        name = self._names[idx]
        calibration_voltage = self._calibration_voltage[idx]
        voltage_sensitivity = self._voltage_sensitivity[idx]

        return {
            name: {
                'updated_1s': calculate_values(
                    measurement.value_1s,
                    measurement.voltage_1s,
                    calibration_voltage,
                    voltage_sensitivity,
                    self._pressure_per_bit
                ),
                'updated_30s': calculate_values(
                    measurement.value_30s,
                    measurement.voltage_30s,
                    calibration_voltage,
                    voltage_sensitivity,
                    self._pressure_per_bit
                )}
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
