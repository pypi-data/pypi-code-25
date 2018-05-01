#!/usr/bin/env python
from setuptools import setup, find_packages
import ec2_sizes

setup(
    name='ec2-sizes',
    version=ec2_sizes.__version__,
    description=ec2_sizes.__doc__,
    author=ec2_sizes.__author__,
    author_email=ec2_sizes.__email__,
    license='BSD',
    url=ec2_sizes.__url__,
    keywords=['amazon', 'ec2'],
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
