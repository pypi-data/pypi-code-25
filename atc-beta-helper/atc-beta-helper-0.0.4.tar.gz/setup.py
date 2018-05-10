#!/usr/bin/env python

from setuptools import setup, find_packages


setup(name='atc-beta-helper',
      version='0.0.4',
      license='MIT',
      platforms='any',
      packages=find_packages(),
      install_requires=[
          'requests==2.18.4',
      ],
      classifiers=[
          'Programming Language :: Python',
          'Operating System :: OS Independent',
      ])
