#!/usr/bin/env python3.6

import os.path as path
from setuptools import find_packages, setup
from importlib import find_loader
from tkml import __VERSION__ as VERSION

with open('./README.md') as fp:
    long_description = fp.read()


setup(
    name='tkml',
    version=VERSION,
    provides=['tkml'],
    description='Tkinter gui representation',
    long_description=long_description,
    author='ℜodrigo ℭacilhας',
    author_email='batalema@cacilhas.info',
    url='https://bitbucket.org/cacilhas/tkml/',
    packages=find_packages(exclude=('tests', 'tests.*')),
    install_requires=[
        'pyyaml==3.12',
    ],
    test_suite='tests',
    tests_require=[
    ],
    classifiers=[
        'Environment :: X11 Applications',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
