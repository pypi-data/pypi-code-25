from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as f:
  long_description = f.read()

setup(
  name = 'bigstate',
  version = '0.0.1',
  description = 'state modules for f5 bigips',
  long_description = long_description,
  url = 'https://github.com/brokenbot/bigstate',
  author = 'David Sanderson',
  author_email = 'dave.d.sanderson@gmail.com',
  classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3'
  ],
  keywords = 'salt f5 bigip ltm',
  packages = ['bigstate'],
  install_requires = ['f5-sdk']
)