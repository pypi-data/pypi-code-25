#!/usr/bin/env python
#
# This file is part of SharedArray.
# Copyright (C) 2014-2018 Mathieu Mirmont <mat@parad0x.org>
#
# SharedArray is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# SharedArray is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SharedArray.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, Extension
import codecs
import glob
import sys
import os

# Fail gracefully if numpy isn't installed
try:
    import numpy
    include_dirs = [numpy.get_include()]
except:
    include_dirs = []

# Get the long description from the README file
here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'SharedArray',
    version = '3.0.0',

    # Description
    description = 'Share numpy arrays between processes',
    long_description = long_description,
    long_description_content_type = 'text/markdown',

    # Contact
    url = 'https://gitlab.com/tenzing/shared-array',
    author = 'Mathieu Mirmont',
    author_email = 'mat@parad0x.org',

    # Classifiers
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: C',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords = 'numpy array shared memory shm',

    # Compilation
    install_requires = ['numpy'],
    ext_modules = [
        Extension('SharedArray',
                  glob.glob(os.path.join('.', 'src', '*.c')),
                  libraries = [ 'rt' ] if sys.platform.startswith('linux') else [],
                  include_dirs = include_dirs)
    ],
)
