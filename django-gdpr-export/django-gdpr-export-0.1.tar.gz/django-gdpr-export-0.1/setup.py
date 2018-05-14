# coding=utf-8
from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    version=0.1,
    name='django-gdpr-export',
    long_description=long_description,
    license='MIT',
    keywords='django gdpr export template file'
)
