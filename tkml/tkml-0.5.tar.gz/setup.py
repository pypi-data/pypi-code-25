#!/usr/bin/env python3.6

from configparser import ConfigParser
import os.path as path
from setuptools import find_packages, setup
from importlib import find_loader

config = ConfigParser()
config.read(path.join(path.dirname(__file__), 'tkml', 'info.ini'))
main_conf = config['tkml']
author_conf = config['author']
deps_conf = config['deps']

with open('./README.md') as fp:
    long_description = fp.read()


setup(
    name='tkml',
    version=main_conf['version'],
    provides=['tkml'],
    description=main_conf['description'],
    long_description=long_description,
    author=author_conf['name'],
    author_email=author_conf['contact'],
    url=config['repo']['url'],
    packages=find_packages(exclude=('tests', 'tests.*')),
    package_data={'tkml': ['info.ini']},
    setup_requires=deps_conf['setup'].split(),
    install_requires=deps_conf['install'].split(),
    test_suite='tests',
    tests_require=deps_conf['test'].split(),
    classifiers=[
        'Environment :: X11 Applications',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
