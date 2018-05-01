# -*- coding: utf-8 -*-

"""Main setup file"""

from setuptools import setup, find_packages

##########################################
##########################################
##########################################
##########################################

setup(name='bi_powerhouse',
      version='0.5.1',
      description='Functions to simplify day to day BI work.',
      url='https://github.com/ksco92/bi_powerhouse',
      author='Rodrigo Carvajal',
      author_email='rodrigocf_92@hotmail.com',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      install_requires=['boto3',
                        'pandas',
                        'pyodbc',
                        'pymysql',
                        'pg8000'
                        ]
      )
