# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 bindh3x <os@bindh3x.io>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

import os
import codecs
import re
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding

here = os.path.abspath(os.path.dirname(__file__))

def find_version(*files):
    """Get the version of Pas"""
    data = None

    with codecs.open(os.path.join(here, *files), 'r', 'utf-8') as fp:
        data = fp.read()

    # Extract the version string.
    match = re.search(r"^__version__ = ['\"](.*?)['\"]", data, re.M)

    if match:
        return match.group(1)
    raise RuntimeError('Cannot extract __version__ string.')

setup(
    name='pas',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=find_version(os.path.join("pas", "__init__.py")),
    description='Secure password manager..',
    # The project's main homepage.
    #url='https://',

    # Author details
    author='bindh3x',
    author_email='<os@bindh3x.io>',

    # Choose your license
    #license='',
    # What does your project relate to?

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['click'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'pas=pas.cli:cli',
        ],
    },
)
