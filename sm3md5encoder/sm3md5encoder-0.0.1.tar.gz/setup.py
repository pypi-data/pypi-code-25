# -*- coding: utf-8 -*-
"""
Created on Thu May  3 16:50:29 2018

@author: yili.peng
"""

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='sm3md5encoder'
      ,version='0.0.1'
      ,description='sm3/md5 encoder'
      ,long_description=readme()
      ,keywords='encoder'
      ,author='Yili Peng'
      ,author_email='yili.peng@outlook.com'
      ,packages=['sm3md5encoder'])
        