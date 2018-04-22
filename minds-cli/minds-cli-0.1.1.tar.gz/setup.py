#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'minds',
    'markdown',
]

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'pytest',
]

setup(
    name='minds-cli',
    version='0.1.1',
    description="cli interface for minds-api",
    long_description=readme + '\n\n' + history,
    author="Bernardas Ališauskas",
    author_email='bernard@hyperio.tech',
    url='https://gitlab.com/granitosaurus/minds-cli',
    packages=find_packages(include=['mindscli', 'mindscli.cli']),
    entry_points={
        'console_scripts': [
            'minds=mindscli.cli.main:cli'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords=['minds.com', 'cli', 'minds'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
