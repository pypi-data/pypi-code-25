#! /usr/bin/env python
# encoding: utf-8

from __future__ import print_function, division, absolute_import

from datapool.landing_zone import LandingZone


def test_order_source_related_yamls():
    rel_paths = [
                 "data/xyz_sensor/xyz_sensor_python/source.yaml",
                 "data/xyz_sensor/xyz_sensor_python/raw/data-001.raw",
                 "data/xyz_sensor/xyz_sensor_python/conversion.py",
                 "datax/sdf",
                 "data/xyz_sensor/source_type.yaml"
                 ]

    expected_sorted = ['data/xyz_sensor/source_type.yaml',
                       'data/xyz_sensor/xyz_sensor_python/source.yaml',
                       'data/xyz_sensor/xyz_sensor_python/conversion.py',
                       'data/xyz_sensor/xyz_sensor_python/raw/data-001.raw']


    sorted_, leftovers = LandingZone.separate_allowed_files(rel_paths)
    assert sorted_ == expected_sorted
    assert leftovers == ["datax/sdf"]
