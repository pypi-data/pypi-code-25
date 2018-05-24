#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='afrigis',
    version='0.1.0.dev1',
    description='Afrigis Python Library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/chris-cmsoft/python-afrigis',
    author='Chris Vermeulen',
    author_email='chris@cmsoft.co.za',

    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        # Project Maturity
        'Development Status :: 1 - Planning',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Topics
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # License
        'License :: OSI Approved :: MIT License',

        # Python Versions
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # Search Keywords
    keywords='Python Afrigis Integration',  # Optional

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required

    install_requires=[],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    # List additional URLs that are relevant to your project as a dict.
    #
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    #
    # Examples listed include a pattern for specifying where the package tracks
    # issues, where the source is hosted, where to say thanks to the package
    # maintainers, and where to support the project financially. The key is
    # what's used to render the link text on PyPI.
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/chris-cmsoft/python-afrigis/issues',
        'Source': 'https://github.com/chris-cmsoft/python-afrigis/',
    },
)
