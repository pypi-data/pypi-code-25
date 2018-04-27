from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    with open(filename) as fh:
        metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", fh.read()))
        return metadata['version']


setup(
    name='Mopidy-PlayerFM',
    version=get_version('mopidy_playerfm/__init__.py'),
    url='https://github.com/ohporter/mopidy-playerfm',
    license='Apache License, Version 2.0',
    author='Matt Porter',
    author_email='mporter@konsulko.com',
    description='Mopidy extension for PlayerFM',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 1.0',
        'Pykka >= 1.1',
        'tornado >= 4.4, < 5',
        'requests >= 2.4.2',
        'beautifulsoup4 >= 4.5',
        'urllib3 >= 1.22',
        'ipaddress >= 1.0.17',
        'pyopenssl >= 16.2.0',
    ],
    entry_points={
        'mopidy.ext': [
            'playerfm = mopidy_playerfm:PlayerFmExtension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
