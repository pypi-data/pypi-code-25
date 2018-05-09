#!/usr/bin/env python
# encoding: utf8

from setuptools import setup, find_packages

setup(
    name='rplotmaker',
    version='1.0.5',
    description='R Plot Maker',
    long_description="Tool to wrap R execution with so that it generates a file specified by options.",
    author='Robert Buchholz, Martin Häcker',
    author_email='rbu@goodpoint.de, spamfaenger@gmx.de',
    license='ISC',
    url='https://gitlab.com/rbuchholz/rplotmaker',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    entry_points=dict(
        console_scripts=[
            'rplotmaker = rplotmaker:main',
        ],
    )
)
