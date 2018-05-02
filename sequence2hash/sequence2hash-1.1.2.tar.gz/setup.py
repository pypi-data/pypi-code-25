#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='sequence2hash',
    version='1.1.2',
    keywords='tuple dict list sequence hash key/value',
    packages=['sequence2hash'],

    url='https://github.com/Cuile/sequence2hash',
    description='This tool converts a valid value in a sequence to a hash and contains a path to a valid value in the key field',
    long_description_content_type='text/markdown',
    long_description=open('README.md', encoding='utf8').read(),

    author='cuile',
    author_email='i@cuile.com'
)
