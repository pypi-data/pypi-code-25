from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name='%(name)s',
  version='0.0.1',
  description='%(name)s - %(description)s',
  long_description=long_description,
  url='%(url)s',
  author='%(author)s',
  author_email='',
  license='%(license)s',
  packages=find_packages(),
  extras_require={
    'dev': ['pytest', 'tox']
  },
  entry_points={
    'console_scripts': [
      '%(name)s=%(name)s.%(name)s:hello',
    ],
  },
  scripts= ['bin/hello-%(name)s']
)
