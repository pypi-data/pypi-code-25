#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
setuptools script file
"""

from __future__ import absolute_import, unicode_literals

from setuptools import setup, find_packages

setup(
    name='aliyunoss2-autoupload',
    namespace_packages=[],
    packages=find_packages('src'),
    package_dir={'': 'src'},

    description='Watch files in a directory and upload them to Aliyun OSS on file writing completed',
    url='https://github.com/tanbro/aliyunoss2-autoupload',
    author='liu xue yan',
    author_email='liu_xue_yan@foxmail.com',

    use_scm_version={
        # guess-next-dev:	automatically guesses the next development version (default)
        # post-release:	generates post release versions (adds postN)
        'version_scheme': 'guess-next-dev',
    },
    setup_requires=['setuptools_scm', 'setuptools_scm_git_archive'],

    install_requires=[
        'argparse;python_version<"2.7"',
        'enum34;python_version<"3.4"',
        'futures;python_version<"3.0"',
        'oss2',
        'PyYAML',
    ],

    entry_points={
        'console_scripts': [
            'aliyunoss2-autoupload = aliyunoss2_autoupload.__main__:main',
        ],
    },

    extras_require={},

    package_data={
        '': ['data/*/*']
    },

    python_requires='>=2.6,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*'
)
