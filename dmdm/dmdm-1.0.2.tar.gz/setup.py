#!/usr/bin/env python

import os

from setuptools import setup

with open('README.md') as readme:
    README = readme.read()

with open('requirements.in') as requirements:
    REQUIREMENTS = requirements.readlines()

setup(
    name='dmdm',
    version='1.0.2',
    packages=['dmdm'],
    install_requires=REQUIREMENTS,
    include_package_data=True,
    license='BSD',
    description='Django MarkDown Mail',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/nim65s/dmdm',
    author='Guilhem Saurel',
    author_email='webmaster@saurel.me',
    python_requires='>=3',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
