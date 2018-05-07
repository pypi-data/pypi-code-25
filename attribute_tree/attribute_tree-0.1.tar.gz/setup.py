#!/usr/bin/env python

from setuptools import setup
from attribute_tree import __version__ as version

classifiers = """
Development Status :: 3 - Alpha
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Topic :: Utilities
""".strip()

description = 'wraps dict into tree-like structure with value access via getattr'
url = 'https://gitlab.com/attu/attribute_tree'
download_url = '{url}/-/archive/{version}/attribute_tree-{version}.tar.gz'.format(
    url=url,
    version=version
)

setup(
    author='Karol Wozniak',
    author_email='karol.wozniak@linuxmail.com',
    classifiers=classifiers.split('\n'),
    description=description,
    download_url=download_url,
    keywords='attribute dictionary tree',
    name='attribute_tree',
    py_modules=['attribute_tree'],
    url=url,
    version=version,
)
