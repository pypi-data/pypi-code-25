#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = ['requests']

setup(
    name='exchanges',
    packages=find_packages(),
    author_email='peablog@qq.com',
    author='Danny0',
    version='0.0.1',
    url='https://github.com/peablog',
    description='coin exchanges restful api',
    install_requires=install_requires
)
