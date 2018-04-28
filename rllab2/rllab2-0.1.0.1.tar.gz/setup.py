# setup.py
from __future__ import absolute_import
from setuptools import setup, find_packages

setup(
    name=u'rllab2',
    version=u'0.1.0.1',
    packages=[i for i in find_packages() if i.startswith('rllab2')],
)
