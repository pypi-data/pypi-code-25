#!/usr/bin/env python
#
# Setup script for configuring, packaging, distributing and installing this Python package.
#
# - Package information
#   - Name:    unified_map
#   - Author:  Robert Haas
#   - Email:   robert.haas@protonmail.com
#   - License: See LICENSE.TXT in the package root directory
#
# - References for best practices in creating Python packages
#   - Python Packaging User Guide (PyPUG): https://packaging.python.org
#   - Python Packaging Authority (PyPA):   https://www.pypa.io
#   - Python Package Index (PyPI):         https://pypi.org
#   - Setuptools:                          https://setuptools.readthedocs.io
#   - Semantic Versioning (SemVer):        https://semver.org

import re
from codecs import open
from os import path

from setuptools import setup


def read_file(filepath):
    """Read content from an UTF-8 encoded text file"""
    with open(filepath, 'r', encoding='utf-8') as file_handle:
        return file_handle.read()


def load_long_description(pkg_dir):
    """Load long description from file README.rst"""
    try:
        filepath_readme = path.join(pkg_dir, 'README.rst')
        return read_file(filepath_readme)
    except Exception:
        raise ValueError('Long description could not be read from README.rst')


def load_version(pkg_dir, pkg_name):
    """Load version from variable __version__ in file __init__.py with a regular expression"""
    try:
        filepath_init = path.join(pkg_dir, pkg_name, '__init__.py')
        file_content = read_file(filepath_init)
        re_for_version = re.compile(r'''__version__\s+=\s+['"](.*)['"]''')
        match = re_for_version.search(file_content)
        version = match.group(1)
        return version
    except Exception:
        raise ValueError('Version could not be read from variable __version__ in file __init__.py')


PKG_NAME = 'unified_map'
PKG_DIR = path.abspath(path.dirname(__file__))

setup(
    # Basic package info
    name=PKG_NAME,
    version=load_version(PKG_DIR, PKG_NAME),
    long_description=load_long_description(PKG_DIR),
    description=('Apply a function to a list of arguments and collect the results '
                 '– serial, parallel or distributed.'),
    author='Robert Haas',
    author_email='robert.haas@protonmail.com',
    url='https://github.com/robert-haas/unified-map',
    license='Apache License, Version 2.0',
    # Keywords (displayed on PyPI)
    keywords=[
        'map',
        'parallel map',
        'parallel for',
        'embarrassingly parallel',
        'perfectly parallel',
        'pleasingly parallel',
        'parallel computing',
        'distributed computing',
    ],
    # Classifiers (available ones listed at https://pypi.org/classifiers)
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities'
    ],
    # Included files: a) Python packages (__init__.py) and b) files defined in MANIFEST.in
    packages=[
        'unified_map',
        'unified_map.univariate',
        'unified_map.multivariate',
    ],
    include_package_data=True,
    # Dependencies that need to be fulfilled
    python_requires='>=3.5',
    # Dependencies that are downloaded
    install_requires=[],
    extras_require={
        'complete': [
            'dask[complete]',
            'joblib',
        ],
        'dev': [
            'dask[complete]',
            'joblib',
            'pytest',
            'pytest-benchmark',
            'pytest-cov',
            'sphinx',
            'sphinx-rtd-theme',
        ],
    },
    # Capability of running in compressed form
    zip_safe=False,
)
