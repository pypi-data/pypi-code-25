# coding: utf-8
import codecs
import os
import sys

try:
    from setuptools import setup
except:
    from distutils.core import setup

"""
打包的用的setup必须引入，
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
 

import sys
if sys.version_info < (2, 5):
    sys.exit('Python 2.5 or greater is required.')
 
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
 
import SendMoney
 
 
with open('README.rst', 'rb') as fp:
    readme = fp.read()
 

VERSION = "0.0.1"

LICENSE = "MIT"

 
setup(
    name='SendMoney',
    version=VERSION,
    description=(
        'test pypi'
    ),
    long_description=readme,
    author='SnowySunny',
    author_email='2549090041@qq.com',
    maintainer='SnowySunny',
    maintainer_email='2549090041@qq.com',
    license=LICENSE,
    platforms=["all"],
    url='https://github.com/snowysunny/Auto_signup_pond',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
    ],
)
