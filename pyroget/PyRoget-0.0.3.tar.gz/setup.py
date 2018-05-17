#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from setuptools import setup
from PyRoget import version

setup(
    name='PyRoget',
    packages=['PyRoget'],
    include_package_data=True,
    version=version,
    description="Python implementation of Roget's thesaurus",
    author="James Wenzel & Phillip R. Polefrone",
    author_email="jameswenzel@berkeley.edu",
    url="https://github.com/jameswenzel/roget-tools",
    download_url=('https://github.com/jameswenzel/roget-tools/tarball/' +
                  version),
    license="GNU",
    keywords=['roget', 'thesaurus', "roget's", 'dictionary', 'similie',
              'similies', 'semantic', 'space'],
    classifiers=[]
)
