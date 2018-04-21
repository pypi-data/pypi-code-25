#!/usr/bin/env python3

from distutils.core import setup
setup(
  name = 'pyphone',
  packages = ['pyphone'], # this must be the same as the name above
  version = '0.1.3',
  description = 'Phonetic manipulation library',
  author = 'Ling Zhang',
  author_email = 'lz@ling.nz',
  url = 'https://github.com/lingz/pyphone', # use the URL to the github repo
  install_requires = [
    'scipy'
  ],
  keywords = ['nlp', 'phonetic', 'ipa'],
)

