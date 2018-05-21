#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pip setup file for bjoda
"""
from setuptools import (
    setup,
    find_packages
)
from bjoda.globals import (
    __version__
)


PROJECT = 'bjoda'
setup(
    name=PROJECT,
    version=__version__,
    description='Better syscalls and commands from python',
    long_description='',
    author='Jacobi Petrucciani',
    author_email='jacobi@mimirhq.com',
    url='',
    py_modules=[PROJECT],
    install_requires=[
        'pexpect'
    ],
    packages=find_packages(),
    include_package_data=True,
    platforms=['Any'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ]
)
