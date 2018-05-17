#!/usr/bin/env python

import sys

from setuptools import find_packages, setup

needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

setup(
    name="watchghost",
    version="0.1.0",
    description="Your invisible but loud monitoring pet",
    url="https://gitlab.com/localg-host/watchghost",
    author="Localghost",
    include_package_data=True,
    packages=find_packages(),
    scripts=['bin/watchghost-check.py', 'bin/watchghost-server.py'],
    install_requires=['tornado', 'aioftp', 'asyncssh', 'watchdog'],
    setup_requires=pytest_runner,
    tests_require=['pytest-cov', 'pytest-flake8', 'pytest-isort', 'pytest'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: System :: Monitoring",
    ],
)
