#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages
from textgears import (
    __author__,
    __author_email__,
    __license__,
    __version__
)

setup(
    name="textgears",
    author=__author__,
    author_email=__author_email__,
    description="A Python API client of textgears.com "
    "for checks English grammar.",
    version=__version__,
    license=__license__,
    packages=find_packages(),
    install_requires=["requests==2.18.4"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2 :: Only",
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities",
    ]
)
