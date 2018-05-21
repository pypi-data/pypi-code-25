# -*- coding: utf-8 -*-

# Stefan Gaillot - xenjee@gmail.com

from setuptools import setup, find_packages


with open('readme.md') as f:
    readme = f.read()

with open('license') as f:
    license = f.read()

setup(
    name='flamepy_sg',
    version='0.0.0.17',
    description='Flame python tools',
    long_description=readme,
    author='Stefan Gaillot',
    author_email='xenjee@gmail.com',
    url='https://github.com/xenjee/flamepy_sg',
    license=license,
    packages=find_packages(exclude=('tests', '*.pyc'))
)
