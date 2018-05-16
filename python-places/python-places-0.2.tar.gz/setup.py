#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('requirements.txt', 'r') as r:
    requirements = r.read().split()

with open('version.txt', 'r') as v:
    version = v.read().strip()

with open('README.md') as f:
    readme = f.read()

setup(
    name='python-places',
    packages=['googleplaces'],
    description=('A set of classes used for interacting with the Google Places API'),
    long_description=readme,
    version=version,
    author='Alexander J. Botello',
    author_email='alexander.botello@g.austincc.edu',
    url='https://github.com/alexbotello/python-places',
    install_requires=requirements,
    license='MIT'
)