#!/usr/bin/env python

from setuptools import setup, find_packages

import sys

setup(name='txThings',
      version='0.3.0',
      description='CoAP protocol implementation for Twisted Framework',
      author='Maciej Wasilak',
      author_email='wasilak@gmail.com',
      url='https://github.com/siskin/txThings/',
      packages=find_packages(exclude=["*.test", "*.test.*"]),
      install_requires = [
          'twisted>=14.0.0',
          'six>=1.10.0',
          'py2-ipaddress>=3.4.1;python_version<"3.0"' ]
     )
