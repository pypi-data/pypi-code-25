from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name='apldx_test',
  version='0.0.2',
  description='apldx_test - Test to delete and remake package',
  long_description=long_description,
  url='',
  author='',
  author_email='',
  license='MIT',
  packages=find_packages(),
  extras_require={
    'dev': ['pytest', 'tox']
  },
  entry_points={
    'console_scripts': [
      'apldx_test=apldx_test.apldx_test:hello',
    ],
  },
  scripts= ['bin/hello-apldx_test']
)
