#!/usr/bin/env python

from setuptools import setup, find_packages

LONG_DESCRIPTION = """
This module provides Python parent classes for 
domain-level strand displacement programming:
  - SequenceConstraint
  - DL_Domain
  - SL_Domain
  - DSD_Complex
  - DSD_Reaction
  - DSD_RestingSet
"""

setup(
    name='dsdobjects',
    version='0.5.2',
    description='base classes for DSD design',
    long_description=LONG_DESCRIPTION,
    author='Stefan Badelt',
    author_email='badelt@caltech.edu',
    license='MIT License',
    packages=['dsdobjects', 'dsdobjects.parser'],
    test_suite='tests',
)

