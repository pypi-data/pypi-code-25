#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


readme = open('README.md').read()
requirements = open('requirements.txt').readlines()
VERSION = open('VERSION').read().strip()

setup(
    name='statsdecor',
    version=VERSION,
    description='A set of decorators and helper methods '
                'for adding statsd metrics to applications.',
    long_description=readme + '\n\n',
    author='Mark Story',
    author_email='markstory@freshbooks.com',
    url='https://github.com/freshbooks/statsdecor',
    packages=find_packages(exclude=['test*']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='statsd, stats',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests'
)
