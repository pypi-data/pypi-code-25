#!/usr/bin/env python

from setuptools import setup

requires=['numpy', 'sympy', 'pylatex']

setup(name='MathMonkey',
      version='0.1',
      description='A repetitive maths practice system.',
      author='Iztok Kucan',
      author_email='iztok.kucan@gmail.com',
      url='https://github.com/ikucan/MathMonkey',
      packages=['l0'],
     )
