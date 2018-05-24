#!/bin/env python

import os
from setuptools import setup

name = 'django-k8s'
version = '0.1'
readme = os.path.join(os.path.dirname(__file__), 'README.rst')
with open(readme) as readme_file:
    long_description = readme_file.read()

setup(
    name = name,
    version = version,
    description = 'Integration between Django and Kubernetes.',
    long_description = long_description,
    author = 'Ben Timby',
    author_email = 'btimby@gmail.com',
    url = 'http://github.com/btimby/' + name + '/',
    license = 'MIT',
    packages = [
        "django_k8s",
    ],
    classifiers = (
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)