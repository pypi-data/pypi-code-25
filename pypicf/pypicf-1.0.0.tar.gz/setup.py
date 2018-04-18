#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages
from pypicf import __author__, __version__

description = "The pypicf is an interactive tool that asks some "
"questions about the PYPI Classifiers of your Pyt "
"hon product, and then generates classifiers list "
"for the insert to the setup.py script."

with open("requirements.txt", "r") as fp:
    requires = fp.read().strip().split("\n")

with open("README.rst", "r") as fp:
    long_description = fp.read()

setup(
    name="pypicf",
    author=__author__,
    description=description,
    long_description=long_description,
    version=__version__,
    license="MIT License",
    packages=find_packages(),
    install_requires=requires,
    entry_points={
        "console_scripts": [
            "pypicf=pypicf.__main__:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2 :: Only",
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities",
    ]
)
