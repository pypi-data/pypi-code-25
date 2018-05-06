#!/usr/bin/env python
from __future__ import unicode_literals
# -*- coding: UTF-8 -*-

"""
Author: Shivam Gupta
Description:
"""

import os
import sys
import time
import unittest
from setuptools import Command
from distutils.core import setup


def get_files(root):
    for dirname, dirnames, filenames in os.walk(root):
        for filename in filenames:
            yield os.path.join(dirname, filename)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


MODULE = "addition"
PREFIX = "math"


setup(
    name='%s_%s' % (PREFIX, MODULE),
    version='1.0',
    packages=['addition'],
    url='https://www.github.com/shivamzaz/addition',
    license='MIT',
    author='Shivam Gupta',
    author_email='shivam.gupta712@gmail.com',
    description='Math Addition',
    zip_safe=False,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Office/Business',
    ],
)
