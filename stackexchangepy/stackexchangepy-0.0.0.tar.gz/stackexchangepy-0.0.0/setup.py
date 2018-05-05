from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='stackexchangepy',
    version='0.0.0',
    description='Stackexchange API Client',
    url='https://github.com/monzita/numerix',
    author='Monika Ilieva',
    author_email='hidden@hidden.com',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Topic :: Software Development :: Build Tools',
      'Programming Language :: Python :: 3.6'
    ],

    keywords='stackexchange api client',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'venv']),
)