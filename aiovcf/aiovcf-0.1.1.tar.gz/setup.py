#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

history = ""

with open('dev-requirements.txt') as dev_requirements_file:
    tests_require = [r.strip() for r in dev_requirements_file.readlines()]

setup(
    name="aiovcf",
    version='0.1.1',

    package_dir={
        '': 'src'
    },

    packages=[
    ],

    include_package_data=True,

    package_data={
    },

    install_requires=[
        "aiofiles",
        "related",
        "antlr4-python3-runtime",
    ],

    setup_requires=[
        'pytest-runner',
    ],

    license="MIT license",

    keywords='',
    description="aiovcf",
    long_description="%s\n\n%s" % (readme, history),

    entry_points={
    },

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
