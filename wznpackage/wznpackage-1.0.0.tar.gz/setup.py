# -*- coding: utf-8 -*-
"""
Created on Thu May 24 16:55:36 2018

@author: sony
"""

from setuptools import setup,find_packages

setup(

        name='wznpackage',

        version='1.0.0',

        description='mypackage_by_ZW',
		
		py_modules=['wznpackage'],

        author='Zhining',

        author_email='w_zhining@163.com',

        url='https://github.com',

        packages=find_packages(),

        install_requires=['django', 'mako'],

)