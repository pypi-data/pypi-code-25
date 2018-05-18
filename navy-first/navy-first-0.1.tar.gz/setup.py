#!/usr/bin/env python3
"""first project"""
from setuptools import find_packages,setup

setup(name = 'navy-first',
    version ='0.1',
    description ='navy  module',
    long_description = 'A test module for our book.',
    platforms =['linux'],
    author = 'navy',
    author_email ='whj001@126.com',
    license = 'MIT',
    packages = find_packages()
    )

