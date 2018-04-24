# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from setuptools import setup

import hifrost

with open('requirements.txt') as f:
    requirements = [l for l in f.read().splitlines() if l]

setup(
    name='hifrost',
    version=hifrost.__version__,
    description='ZaihuiHui Bifrost',
    long_description='',
    author='ZaiHui',
    author_email='llk@kezaihui.com',
    url='https://github.com/zaihui',
    license='MIT License',
    packages=['hifrost'],
    install_requires=requirements,
)
