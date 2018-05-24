#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 02/03/2018 16:02
# @Author  : Zhang Lei
# @Site    : 
# @File    : setup
# @Software: PyCharm
from setuptools import setup
import ast


def get_version(fname):
    with open(fname) as f:
        source = f.read()
    pmodule = ast.parse(source)
    for e in pmodule.body:
        if isinstance(e, ast.Assign) and \
                len(e.targets) == 1 and \
                e.targets[0].id == '__version__' and \
                isinstance(e.value, ast.Str):
            return e.value.s
    raise RuntimeError('__version__ not found')

setup(
        name='common-ops',
        packages=['ops'],
        description='Ops Common libraries',
        version=get_version('ops/version.py'),
        url='http://git.patsnap.com/devops/ops-libraries',
        author='ZhangLei',
        author_email='zhanglei@patsnap.com',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Libraries :: Application Frameworks',
        ],
        keywords=['python', 'common-libraries'],
        install_requires=[
            "boto3"
        ],
        include_package_data=True,
        zip_safe=False
)