#!/usr/bin/env python  
from __future__ import print_function  
from setuptools import setup, find_packages  
import sys  
  
setup(  
    name="echosun",  
    version="0.1",  
    author="Echo Sun",  
    author_email="echosun1996@126.com",  
    description="a set of functions",  
    long_description=open("README.rst").read(),  
    license="MIT",  
    url="https://github.com/echosun1996",  
    packages=['echosun'],  
##    install_requires=[  
##        "beautifulsoup4",  
##        lxml_requirement  
##        ],  
    classifiers=[  
        "Environment :: Web Environment",  
        "Intended Audience :: Developers",  
        "Operating System :: OS Independent",  
        "Topic :: Text Processing :: Indexing",  
        "Topic :: Utilities",  
        "Topic :: Internet",  
        "Topic :: Software Development :: Libraries :: Python Modules",  
        "Programming Language :: Python",  
        "Programming Language :: Python :: 2",  
        "Programming Language :: Python :: 2.6",  
        "Programming Language :: Python :: 2.7",  
    ],  
)  
