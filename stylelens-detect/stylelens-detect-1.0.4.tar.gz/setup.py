# coding: utf-8

"""
    stylelens-detect
"""


import sys
from setuptools import setup, find_packages

NAME = "stylelens-detect"
VERSION = "1.0.4"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["grpcio", "grpcio-tools"]

setup(
    name=NAME,
    version=VERSION,
    description="stylelens-detect",
    author_email="master@bluehack.net",
    url="",
    keywords=["BlueLens", "stylelens-detect"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    """
)
