#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 15:24:18 2018

@author: zxs107020
"""

from setuptools import setup

setup(name = 'zxs',
      version = '11',
      description = 'A package for data science made easy',
      url = 'https://github.com/zxs107020/zxs',
      author = 'zxs107020',
      author_email = 'zxs107020@gmail.com',
      license = 'self',
      packages = ['zxs'],
      entry_points = {'console_scripts': ['zxs = zxs.__main__:main']},
      zip_safe = False)
