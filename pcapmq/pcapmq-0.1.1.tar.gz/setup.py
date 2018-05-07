#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'hbmqtt>=0.9.1', 'pypcap>=1.2.1', 'dpkt>=1.9.1']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Jason Hu",
    author_email='awaregit@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Publish PCAP result to MQTT",
    entry_points={
        'console_scripts': [
            'pcapmq=pcapmq.cli:main',
        ],
    },
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='pcapmq',
    name='pcapmq',
    packages=find_packages(include=['pcapmq']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/awarecan/pcapmq',
    version='0.1.1',
    zip_safe=False,
)
