# -*- coding: utf-8 -*-
from __future__ import print_function

from os import chdir
from os.path import abspath, dirname

from setuptools import find_packages, setup

chdir(dirname(abspath(__file__)))

setup(
    name='flask-authnz-ldap-rbac',
    version_command=('git describe --tags --dirty', 'pep440-git-full'),
    description='Uses AuthN/AuthZ environment variables from Apache mod_authnz_ldap to enforce access controls on Flask apps',
    author='Brandon Davidson',
    author_email='brad@oatmail.org',
    url='https://github.com/brandond/flask-authnz-ldap-rbac',
    packages=find_packages(),
    include_package_data=False,
    install_requires=[
        'flask',
    ],
    extras_require={
        'dev': [
            'setuptools-version-command',
        ]
    },
    license='Apache',
    python_requires='>=2.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP',
        'Framework :: Flask'
    ],
)
