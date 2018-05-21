#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.7', ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Bjoern Kolja Mielsch",
    author_email='kolja.mielsch@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Small CLI tool that customizes the conda create command.",
    entry_points={
        'console_scripts': [
            'ccc=custom_conda_create.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='custom_conda_create',
    name='custom_conda_create',
    packages=find_packages(include=['custom_conda_create']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/bk-m/custom_conda_create',
    version='0.1.0',
    zip_safe=False,
)
