#!/usr/bin/env python
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.

from setuptools import setup, find_packages
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='hubtype',
    version='0.1.2',
    description='Cli tool to automate common tasks with Hubtype Bots',
    package_data={
        '': ['README.md'],
    },
    long_description=read('README.md'),
    author='Hubtype',
    author_email='info@hubtype.com',
    url='http://www.hubtype.com',
    # download_url='http://www.metis.ai/downloads',
    # keywords='',
    # classifiers=[],
    # license='',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click ==6.6',
        'click-log ==0.1.4',
        'sh ==1.11',
        'requests ==2.18.4',
        'inquirer ==2.2.0',
    ],
    entry_points='''
        [console_scripts]
        ht=hubtype.ht:ht
    ''',
)