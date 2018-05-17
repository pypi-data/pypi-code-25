#!/usr/bin/env python  
from __future__ import print_function
from setuptools import setup, find_packages
import sys
import eng2chs

setup(
    name="eng2chs",
    version="0.10.5",
    author="smvlboy",
    author_email="smvlboy@outlook.com",
    description="a moudle used to translate english to chinese",
    url="https://pypi.org/project/eng2chs/#description",
	packages=['eng2chs'],
    install_requires=[
        'urllib3',
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)  