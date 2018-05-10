#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['six', ]

setup_requirements = ['pytest-runner', 'freezegun']

test_requirements = ['pytest', ]

setup(
    author="Kalibrr Technology Ventures, Inc.",
    author_email='hirenow@kalibrr.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Sliding rate limiter using memory or a distributed Redis backend.",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='sliding_rate_limiter',
    name='sliding_rate_limiter',
    packages=find_packages(include=['sliding_rate_limiter', 'sliding_rate_limiter.backends']),
    setup_requires=setup_requirements,
    extras_requires={
        'redis': ['redis', ]
    },
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/kalibrr/sliding_rate_limiter',
    version='2.0.0',
    zip_safe=False,
)
