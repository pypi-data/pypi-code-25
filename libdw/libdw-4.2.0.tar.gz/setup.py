#!/usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
from os import path

here=path.abspath(path.dirname(__file__))

with open(path.join(here,'README.rst'), encoding='utf-8') as f:
    long_description=f.read()

setup(name='libdw',
      version='4.2.0',
      description='The Digital World Code Distribution',
      long_description=long_description,
      author='Oka Kurniawan',
      author_email='oka_kurniawan@sutd.edu.sg',
      license='MIT',
      url='http://www.sutd.edu.sg',
      #py_modules = ['firebase'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Topic :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
      ],
      keywords='simulation library package',
      packages = find_packages(exclude=['contrib','docs','tests']),
      python_requires='>=3',
      install_requires=[
        'requests',
        'gcloud',
        'oauth2client',
        'requests_toolbelt',
        'python_jwt',
      ], 
      )
