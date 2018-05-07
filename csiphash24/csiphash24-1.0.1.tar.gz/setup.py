#!/usr/bin/env python

from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    readme = f.read()

if __name__ == '__main__':
    setup(
        name='csiphash24',
        version='1.0.1',
        url='https://github.com/alexpirine/python-csiphash24',
        license='MIT',
        author='Alexandre Syenchuk',
        author_email='alex@pirine.fr',
        description='A CFFI-based implementation of SipHash24',
        long_description=readme,
        long_description_content_type='text/markdown',
        packages=find_packages(exclude=['test']),
        python_requires='>=3.6',
        setup_requires=["cffi>=1.4.0"],
        cffi_modules=["build_csiphash24.py:ffibuilder"],
        install_requires=["cffi>=1.4.0"],
        classifiers=[
            'Intended Audience :: Developers',
            'Programming Language :: Python :: 3.6',
        ],
    )
