#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
from setuptools import setup, find_packages

setup(
    name='credstash-cache',
    version='0.0.2',
    description="Cache credstash secrets into memory.",
    keywords='credstash cache'.split(),
    author='Mike Bjerkness',
    author_email='mike.bjerkness@centriam.com',
    maintainer='Mike Bjerkness',
    maintainer_email='mike.bjerkness@centriam.com',
    url='https://github.com/centriam/credstash-cache',
    license='MIT',
    package_dir={'credstash_cache': 'credstash_cache'},
    install_requires=['credstash',],
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Security',
        'Topic :: Utilities',
    ],
    zip_safe=False,
)
