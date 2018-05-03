#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from setuptools import setup


"""
Copied from https://github.com/encode/apistar/blob/master/setup.py
"""


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with open(os.path.join(package, '__init__.py')) as f:
        init_py = f.read()

    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


def get_long_description(long_description_file):
    """
    Read long description from file.
    """
    with open(long_description_file, encoding='utf-8') as f:
        long_description = f.read()

    return long_description


version = get_version('nanny')


setup(
    name='nanny',
    version=version,
    url='https://github.com/njncalub/nanny',
    license='MIT',
    description='Simple utility to babysit your files and folders',
    keywords='automated files organizer',
    long_description=get_long_description('README.md'),
    long_description_content_type='text/markdown',
    author='Nap Joseph Calub',
    author_email='njncalub+nanny@gmail.com',
    packages=get_packages('nanny'),
    package_data=get_package_data('nanny'),
    install_requires=[],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
