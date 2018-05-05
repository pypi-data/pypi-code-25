#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tec.ic.ia.p1.g07',
      version='1.0.0',
      py_modules=['tec.ic','tec.ic.ia','tec.ic.ia.p1','tec.ic.ia.p1.g07'],
      description='Programa que entrena distintos modelos de clasificacion de votantes para las elecciones presidenciales en Costa Rica 2018.',
      author='Trifuerza',
      author_email='',
      url='https://github.com/mamemo/Voting-Prediction',
      packages= find_packages(exclude=['docs', 'tests*']),
     )

      

      
