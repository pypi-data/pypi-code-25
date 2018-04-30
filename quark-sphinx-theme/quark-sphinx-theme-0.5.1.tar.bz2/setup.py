#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from io import open
import os
import sys
from setuptools import setup, find_packages

dist_dir = os.path.dirname(os.path.abspath(__file__))
readme = os.path.join(dist_dir, 'README.rst')
with open(readme, 'r', encoding='utf-8') as f:
    long_description = f.read()

sys.path.insert(0, os.path.join(dist_dir, 'src', 'quark_sphinx_theme'))
from __version__ import __version__  # noqa
del sys.path[0]

tests_require = ['html5lib', 'tinycss']
if sys.version_info[:2] < (3, 3):
    tests_require.append('mock')

setup(
    name='quark-sphinx-theme',
    version=__version__,
    description='A Sphinx theme designed for QTextBrowser',
    long_description=long_description,
    url='https://gitlab.com/fkrull/quark-sphinx-theme',
    author='Felix Krull',
    author_email='f_krull@gmx.de',
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Sphinx :: Theme',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Software Development :: Documentation',
    ],
    zip_safe=False,
    install_requires=['sphinx>=1.1'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*',

    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    entry_points={
        'sphinx_themes': [
            'path = quark_sphinx_theme:get_path',
        ]
    },

    test_suite='test',
    tests_require=tests_require,
)
