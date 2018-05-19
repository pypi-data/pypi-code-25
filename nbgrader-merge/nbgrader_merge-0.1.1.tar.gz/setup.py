#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    author="Hugo Castilho",
    author_email='hcastilho@lisbondatascience.org',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Merge nbgrader exercise notebooks",
    entry_points={
        'console_scripts': [
            'nbgrader_merge=nbgrader_merge.__main__:main',
        ],
    },
    license="MIT license",
    include_package_data=True,
    name='nbgrader_merge',
    packages=find_packages(include=['nbgrader_merge']),
    url='https://github.com/hcastilho/nbgrader_merge',
    version='0.1.1',
    zip_safe=False,
)
