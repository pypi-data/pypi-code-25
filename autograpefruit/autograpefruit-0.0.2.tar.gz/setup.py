#!/usr/bin/env python3

from distutils.core import setup

MAJOR_VERSION='0'
MINOR_VERSION='0'
PATCH_VERSION='2'

VERSION = "{}.{}.{}".format(MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION)

setup(
    name = 'autograpefruit',
    packages = ['agf','agf.gmaps','agf.photos','agf.streetview'],
    package_dir = {'': 'src/python'},
    version = VERSION,
    description = 'Tools for performing automated neighborhood analysis from open-source data.',
    author = 'Steve Norum',
    author_email = 'sn@drunkenrobotlabs.org',
    url = 'https://github.com/stevenorum/autograpefruit',
    download_url = 'https://github.com/stevenorum/autograpefruit/archive/{}.tar.gz'.format(VERSION),
    keywords = ['python','machine learning','google maps','google streetview'],
    classifiers = [],
)
