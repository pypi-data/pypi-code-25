# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 15:40:43 2018

@author: i
"""

from setuptools import setup,find_packages
setup(
  name = 'crns_cipher',
  version = '0.1',
  description = 'Ciphers',
  author = 'Nirav Shah',
  author_email = '15ce128@charusat.edu.in',
  license='MIT',
  packages=find_packages(),
  install_requires=['numpy','sympy']
)