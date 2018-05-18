#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Zirpu's utility package.  Mostly just 1-off, but useful, scripts.

import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


HERE = os.path.abspath(os.path.dirname(__file__))

install_requires = [i.strip() for i in open(HERE + '/requirements.txt')
                    if not i.startswith(('#', '-r'))]

tests_require = [i.strip() for i in open(HERE + '/test-requirements.txt')
                 if not i.startswith(('#', '-r'))]


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='zirpu-utils',
    description="Zirpu's Misc. Utilities.",
    long_description=open(HERE + '/README.rst').read(),

    version='0.7.0',

    author='Allan Bailey',
    author_email='zirpubolci@gmail.com',

    url="http://zirpu.org",

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Operating System :: POSIX :: Linux',
        'Topic :: Utilities',
    ],
    # keywords='i dunno what to put here. so there.',

    cmdclass={'test': PyTest},
    packages=find_packages(exclude=['tests']),
    zip_safe=False,

    include_package_data=True,

    install_requires=install_requires,
    tests_require=tests_require,

    # scripts=[
    #     #'scripts/zirpu.self-signed.ssl.setup.sh',
    #     #'scripts/decimal_time.py'
    # ],

    # alternative scripts
    entry_points={
        'console_scripts': [
            'decimal_time = zirpu.time:main',
            'decimal_time.py = zirpu.time:main'
        ]
    },

)
