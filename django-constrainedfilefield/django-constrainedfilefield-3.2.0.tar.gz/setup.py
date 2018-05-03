#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import find_packages, setup

from constrainedfilefield import __version__

REPO_URL = "https://github.com/mbourqui/django-constrainedfilefield/"

README = ''
for ext in ['md', 'rst']:
    try:
        with open(os.path.join(os.path.dirname(__file__), 'README.' + ext)) as readme:
            README = readme.read()
    except FileNotFoundError as fnfe:
        pass

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

FILETYPE_REQUIRE = [
    'python-magic-bin; platform_system=="Windows"',
    'python-magic >= 0.4.2; platform_system!="Windows"',
]

IMAGE_REQUIRE = [
    'Pillow >= 4.0.0'
]

TESTS_REQUIRE = FILETYPE_REQUIRE + IMAGE_REQUIRE

setup(
    name='django-constrainedfilefield',
    version=__version__,
    author='Marc Bourqui',
    author_email='pypi.kemar@bourqui.org',
    license='BSD',
    description="This Django app adds a new field type, ConstrainedFileField, that has the "
                "capability of checking the document size and type.",
    long_description=README,
    url=REPO_URL,
    download_url=REPO_URL + 'releases/tag/v' + __version__,
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.po', '*.mo'],
    },
    install_requires=[
        'django>=1.8,<2.0; python_version<="3.0"',
        'django>=1.8; python_version>="3.4"',
    ],
    tests_require=TESTS_REQUIRE,
    extras_require={
        'filetype': FILETYPE_REQUIRE,
        'image': IMAGE_REQUIRE,
        'coverage': TESTS_REQUIRE,  # Used for travis
    },
    keywords='django filefield validation file',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Utilities',
    ]
)
