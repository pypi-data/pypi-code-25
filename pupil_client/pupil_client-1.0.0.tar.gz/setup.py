#!/usr/bin/env python

import imp

from setuptools import setup, find_packages

version = imp.load_source('pupil_client.version', 'pupil_client/version.py')


setup(name='pupil_client',
      version=version.version,
      packages=find_packages(),
      install_requires=['zmq', 'msgpack'],
      )
