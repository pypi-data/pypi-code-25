#!/usr/bin/env python
from setuptools import setup

setup(
    name='afb_search',
    version='1.0.0',
    description='CLI to search enrolled Alexa for Business Devices',
    author='Scott Odle',
    author_email='scott@sjodle.com',
    url='https://github.com/sodle/afb_search',
    download_url='https://github.com/sodle/afb_search/archive/1.0.0.tar.gz',
    license='GPL v3',
    packages=['afb_search'],
    install_requires=[
        'boto3',
        'docopt'
    ],
    entry_points={
        'console_scripts': [
            'afb_search = afb_search.__main__:_main'
        ]
    }
)
