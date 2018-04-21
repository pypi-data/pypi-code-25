#!/usr/bin/env python
from setuptools import setup

setup(
    name='git-gerp',
    version='0.1.1',
    description='git grep wrapper for arguments re-ordering, that can use options after filenames',
    long_description=open('README.rst').read(),
    url='https://github.com/htaketani/git-gerp',
    author='htaketani',
    author_email='h.taketani@gmail.com',
    license='MIT',
    py_modules=['git_gerp'],
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Version Control",
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            'git-gerp=git_gerp:main',
        ],
    },
)
