#!/usr/bin/env python

from setuptools import setup

setup(
    setup_requires=['pbr'],
    pbr=True,
    py_modules=['aiomsgpack', ],
    include_package_data=True,
    test_suite='test_aiomsgpack',
)
