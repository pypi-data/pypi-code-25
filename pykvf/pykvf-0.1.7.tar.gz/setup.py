#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='pykvf',
    version='0.1.7',
    description='null',
    author='banixc',
    author_email='banixc@qq.com',
    url=' ',
    py_modules=['pykvf'],
    packages=find_packages(),
    install_requires=[
        'pymysql',
        'toml'
    ],
)
