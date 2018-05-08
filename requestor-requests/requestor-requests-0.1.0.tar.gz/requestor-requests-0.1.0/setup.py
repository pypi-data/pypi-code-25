#!/usr/bin/env python

from distutils.core import setup

setup(name='requestor-requests',
      version='0.1.0',
      description='Requestor Helper to request package',
      author='Elio Rincon',
      author_email='eliosf27@gmail.com')

from setuptools import setup

import sys


install_requires = [
    "pkginfo >= 1.4.2",
    "requests >= 2.18.4, != 2.15, != 2.16",
    "setuptools >= 0.7.0",
]


setup(
    name='requestor-requests',
    version='0.1.0',
    description='Requestor Helper to request package',
    author='Elio Rincon',
    author_email='eliosf27@gmail.com',
    install_requires=install_requires,
)
