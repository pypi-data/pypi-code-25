#!/usr/bin/env python

from setuptools import setup, find_packages
import setuptools

import io

with io.open('README.rst', encoding='utf-8') as f:
    long_description = f.read()


setup(
    long_description=long_description,
    long_description_content_type="text/x-rst",
    setup_requires=['setuptools_scm'],
    use_scm_version={'write_to': 'src/sphinx_autodoc_variants/_version.py'},
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
)
