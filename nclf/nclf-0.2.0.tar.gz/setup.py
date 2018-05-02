#!/usr/bin/env python

from distutils.core import setup

setup(
    name='nclf',
    version='0.2.0',
    description='nclf-python is an implementation of the New Command Line Format (NCLF) in python',
    author='Peter Kuma',
    author_email='peter.kuma@fastmail.com',
    license='Public Domain',
    url='https://github.com/peterkuma/nclf-python',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
    ],
    scripts=['nclf', 'as_s'],
    py_modules=['nclf'],
)
