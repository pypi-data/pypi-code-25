#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tec.ic.ia.pc2.g07.main',
      version='1.0.0',
      py_modules=['tec.ic','tec.ic.ia','tec.ic.ia.pc2','tec.ic.ia.pc2.g07','tec.ic.ia.pc2.g07.main'],
      description='This reposiory contains the Artificial Intelligence\'s short-project 2 and 3. Course imparted on Instituto Tecnologico de Costa Rica by Juan Esquivel. On this project we will explore search algorithms to solve path-finding problems.',
      author='Trifuerza',
      author_email='',
      url='https://github.com/mamemo/Path-finding',
      packages= find_packages(exclude=['docs', 'tests*']),
     )
