#!/usr/bin/env python
import os

import setuptools


ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)))
with open(os.path.join(ROOT, 'README.rst')) as file:
    description = file.read()


setuptools.setup(
    name='mrst',
    version='0.3.0',
    description='Augments rst docs',
    long_description=description,
    author='Tim Simpson',
    license='MIT',
    py_modules=['mrst'],
)
