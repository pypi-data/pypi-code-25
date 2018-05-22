#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2018
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('jms_storage/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open(os.path.join(BASE_DIR, 'README.md'), 'rb') as f:
    readme = f.read().decode('utf-8')

with open(os.path.join(BASE_DIR, 'requirements.txt'), 'r') as f:
    requirements = [x.strip() for x in f.readlines()]

setup(
    name='jms-storage',
    version=version,
    keywords=['jumpserver', 'storage', 'oss', 's3', 'elasticsearch'],
    description='Jumpserver storage python sdk tools',
    long_description=readme,
    license='MIT Licence',
    url='http://www.jumpserver.org/',
    author='Jumpserver team',
    author_email='support@fit2cloud.com',
    packages=['jms_storage'],
    include_package_data=True,
    install_requires=requirements,
    platforms='any',
)
