#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 02/03/2018 14:31
# @Author  : Liozza
# @Site    : 
# @File    : setup
# @Software: PyCharm

from setuptools import setup

setup(
        name='jarvis-helper',
        packages=['jarvis'],
        description='Ops management system --- JARVIS',
        version='1.0.1',
        url='https://github.com/liozzazhang/JARVIS',
        author='ZhangLei',
        author_email='zlprasy@gmail.com',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Libraries :: Application Frameworks',
        ],
        keywords=['automation', 'management'],
        platform='python2.7',
        install_requires=[
            "pyyaml",
            'botocore',
            'dictdiffer',
            'ops'
        ],
        include_package_data=True,
        zip_safe=False,
        scripts=['bin/jarvis']
)
