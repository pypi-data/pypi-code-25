#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup

version = "1.0.0"

setup_data = {
    'name': 'py-settings',
    'version': version,
    'author': 'Mikal de Langen',
    'author_email': 'info@mikaldelangen.nl',
    'url': 'https://github.com/mikaldl/py-settings',
    'description': 'Simplistic class for simple class settings inside python',
    'long_description': """Simplistic class for simple class settings inside python""",
    'packages': ['pysettings'],
    'license': "MIT",
    'platforms': "All",
    'classifiers': [
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
    ],
}

args = ()
kwargs = setup_data
setup(*args, **kwargs)
