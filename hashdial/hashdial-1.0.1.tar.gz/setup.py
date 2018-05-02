#!/usr/bin/env python

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='hashdial',
    version='1.0.1',
    description='A module implementing hash based decision making',
    long_description="""Implements, through hashing, decision making that is deterministic on input, but probabilistic across a set of inputs.

For example, suppose a set of components in a distributed system wish to emit a log entry for 1% of requests - but each
component should log the *same* 1% of requests, they could do so as such::

    if hashdial.decide(request.id, 0.01):
        log_request(request)

Take a look at `the documentation <http://py-hashdial.readthedocs.io/en/latest/>`__ for more.
""",  # noqa
    long_description_content_type='text/x-rst',
    url='https://github.com/scode/py-hashdial',
    author='Peter Schuller',
    author_email='peter.schuller@infidyne.com',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='hashdial hashing decision',
    packages=find_packages(exclude=['docs', 'scripts', 'tests']),

    python_requires='>3.4',

    install_requires=[
    ],

    extras_require={
        # see requirements-dev.in/requirements-dev.txt
    },

    project_urls={
        'Documentation': 'http://py-hashdial.readthedocs.io/en/latest/',
        'Source': 'https://github.com/scode/py-hashdial',
    },
)
