#!/usr/bin/env python
"""Distutils installer for rabbitfixture."""

import sys

from setuptools import setup, find_packages


install_requires = [
    'amqp >= 2.0.0',
    'fixtures >= 0.3.6',
    'setuptools',
    'testtools >= 0.9.12',
    ]
if sys.version_info[0] < 3:
    install_requires.append('subprocess32')

setup(
    name='rabbitfixture',
    version="0.4.0",
    packages=find_packages('.'),
    package_dir={'': '.'},
    include_package_data=True,
    zip_safe=False,
    description='Magic.',
    install_requires=install_requires,
    extras_require={
        'test': [
            'six',
            ],
        })
