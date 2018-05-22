# -*- coding: utf-8 -*-
"""
Created on Tue May  8 13:21:09 2018

@author: yili.peng
"""

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='single_factor_model'
      ,version='0.0.3'
      ,description='factor model'
      ,long_description=readme()
      ,keywords='factor model quant'
      ,lisence='MIT'
      ,author='Yili Peng'
      ,author_email='yili.peng@outlook.com'
      ,packages=['single_factor_model']
      ,zip_safe=False)