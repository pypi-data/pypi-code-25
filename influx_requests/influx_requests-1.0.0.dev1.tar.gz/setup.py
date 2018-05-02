#!/usr/bin/env python3
from setuptools import setup

setup(
    name='influx_requests',
    version='1.0.0.dev1',
    description='monkey patch for requests, that save requests by influxdb',
    author='ttm1234',
    author_email='',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='influx_requests',
    py_modules=['influx_requests'],
)
