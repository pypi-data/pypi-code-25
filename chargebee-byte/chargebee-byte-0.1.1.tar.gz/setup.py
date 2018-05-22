#!/usr/bin/env python

import setuptools
import os
from os.path import abspath, dirname

# allow setup.py to be ran from anywhere
os.chdir(dirname(abspath(__file__)))

setuptools.setup(
    name='chargebee-byte',
    version='0.1.1',
    license='MIT',
    description='Chargebee API library. Made by Byte.nl',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Byte',
    author_email='tech@byte.nl',
    url='https://github.com/ByteInternet/chargebee-byte',
    packages=setuptools.find_packages(include=('chargebee_byte',
                                               'chargebee_byte.*')),
    install_requires=['requests'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
