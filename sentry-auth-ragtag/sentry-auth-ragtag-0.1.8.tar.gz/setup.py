#!/usr/bin/env python
"""
sentry-auth-ragtag
==================

:copyright: (c) 2016 Functional Software, Inc
"""
from setuptools import find_packages, setup

install_requires = [
    'sentry>=7.0.0',
]

tests_require = [
    'mock',
    'flake8>=2.0,<2.1',
]

setup(
    name='sentry-auth-ragtag',
    version='0.1.8',
    author='Ragtag',
    author_email='opensource@ragtag.org',
    url='https://ragtag.org',
    description='Ragtag authentication provider for Sentry',
    long_description=__doc__,
    license='Apache 2.0',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'tests': tests_require},
    include_package_data=True,
    entry_points={
        'sentry.apps': [
            'auth_ragtag = sentry_auth_ragtag',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
