#!/usr/bin/env python3
# coding=utf-8

"""
@version: 0.1
@author: ysicing
@file: dops/setup.py.py 
@time: Apr 27, 14:11
"""

from dops import __version__
from setuptools import setup, find_packages

import sys

version = sys.version_info
error_msg = "dops needs Python>=2.7.13(3.6.4). Found %s" % sys.version

if version.major == 2:
    if version.minor < 7:
        sys.exit(error_msg)
    else:
        if version.micro < 13:
            sys.exit(error_msg)


requires = [
    'click>=4.0,<7.0',
]

setup(
    name='dops',
    version=__version__,
    description='DOPS CLI',
    author='Cloudnative Labs',
    url='https://github.com/ysicing/dops',
    packages=find_packages(),
    package_data={'dops': ['data/cli.json']},
    zip_safe=False,
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'dops = dops.main:cli',
        ]
    },
    license="Apache License 2.0",
    keywords=('kubernetes', 'dops', 'spanda',),
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ),
)