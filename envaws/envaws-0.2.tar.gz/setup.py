#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='envaws',
    version='0.2',
    description='Run application with environment loaded from AWS SSM.',
    author='Andrew Dunai',
    author_email='a@dun.ai',
    url='https://github.com/and3rson/envaws',
    install_requires=[
        'boto3'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'envaws=envaws:entrypoint'
        ]
    }
)
