#!/usr/bin/env python

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='pyemtapi',
      version='1.0',
      description='Python library to access some functionality of the REST API of the Municipal Transport Company of Madrid.',
      long_description=read('README.md'),
      author='Rafa Munoz',
      author_email='rafa93m@gmail.com',
      url='https://github.com/RafaMunoz/pyemtapi',
      packages=['pyemtapi'],
      license='MIT',
      install_requires=['urllib3'],
      keywords='api emt madrid python',
      classifiers=[],
      )

