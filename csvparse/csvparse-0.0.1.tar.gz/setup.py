#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from setuptools import setup, find_packages

with open('csv_parse/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')


with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as changelog_file:
    changelog = changelog_file.read()


setup(
    name='csvparse',
    version=version,
    description='A simple state-machine based CSV parser.',
    long_description=readme + '\n\n' + changelog,
    author='Andrew Gross',
    author_email='andrew.w.gross@gmail.com',
    url='https://github.com/andrewgross/csv_read',
    install_requires=[],
    packages=[n for n in find_packages() if not n.startswith('tests')],
    include_package_data=True,
)
