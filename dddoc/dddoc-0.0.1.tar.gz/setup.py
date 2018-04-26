#!/usr/bin/env python
"""setup file for dddoc"""
from setuptools import (
    setup,
    find_packages
)
from dddoc.globals import (
    __version__
)


PROJECT = 'dddoc'
VERSION = __version__
setup(
    name=PROJECT,
    version=VERSION,
    description='very simple python app documentation generator',
    long_description='very simple python app documentation generator',
    author='Jacobi Petrucciani',
    author_email='jacobi@mimirhq.com',
    url='',
    py_modules=[PROJECT],
    download_url='',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
        'Environment :: Console',
    ],
    platforms=['Any'],
    scripts=[],
    provides=[],
    install_requires=[],
    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'dddoc = dddoc:list_files'
        ]
    }
)
