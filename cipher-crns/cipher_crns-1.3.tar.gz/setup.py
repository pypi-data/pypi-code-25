# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 15:40:43 2018

@author: i
"""

from setuptools import setup,find_packages
setup(
  name = 'cipher_crns',
  version = '1.3',
  description = 'Ciphers',
  author = 'Nirav Shah',
  author_email = '15ce128@charusat.edu.in',
  license='MIT',
  packages=find_packages(),
  install_requires=['numpy','sympy']
)