from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name='squelette',
  version='0.0.2',
  description='squelette - skeleton generator',
  long_description=long_description,
  url='http://appliedstochastics.com',
  author='Ajay Khanna',
  author_email='',
  license='MIT',
  packages=find_packages(),
  extras_require={
    'dev': ['pytest', 'tox']
  },
  scripts=['bin/squelette']
)
