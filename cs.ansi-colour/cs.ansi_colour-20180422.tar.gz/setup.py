#!/usr/bin/env python
from setuptools import setup
setup(
  name = 'cs.ansi_colour',
  description = 'Convenience functions for ANSI terminal colour sequences',
  author = 'Cameron Simpson',
  author_email = 'cs@cskk.id.au',
  version = '20180422',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Development Status :: 6 - Mature', 'Environment :: Console', 'Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Terminals', 'Intended Audience :: Developers', 'Operating System :: OS Independent', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'],
  install_requires = [],
  keywords = ['python2', 'python3'],
  long_description = 'Mapping and function for adding ANSI terminal colour escape sequences\nto strings for colour highlighting of output.',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.ansi_colour'],
)
