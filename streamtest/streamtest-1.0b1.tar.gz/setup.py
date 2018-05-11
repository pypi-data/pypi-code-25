#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages
from streamtest import (
    __author__,
    __author_email__,
    __version__,
    __license__
)

with open("README.rst", "r") as fp:
    readme = fp.read()

setup(
    name="streamtest",
    author=__author__,
    author_email=__author_email__,
    description="Python unittest.TestCase for testing the output of "
                "standard stream(stdout, stderr)",
    long_description=readme,
    version=__version__,
    license=__license__,
    url="https://github.com/alice1017/streamtest",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Testing :: Unit",
    ]
)
