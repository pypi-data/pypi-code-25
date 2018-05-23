# coding: utf-8

"""
    bl-db-product-amz-best
    Utility package for bl-db-product-amz-best(DB)

"""

import sys
from setuptools import setup, find_packages

NAME = "bl-db-product-amz-best"
VERSION = "0.0.2"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["pymongo"]

setup(
    name=NAME,
    version=VERSION,
    description="bl-db-product-amz-best",
    author_email="rano@bluehack.net",
    url="",
    keywords=["BlueLens", "bl-db-product-amz-best"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    """
)
