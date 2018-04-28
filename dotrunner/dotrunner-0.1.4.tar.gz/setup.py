# -*- coding: utf-8 -*-

from dotrunner import VERSION
from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='dotrunner',
    version=VERSION,
    description='Links dotfiles',
    long_description=readme,
    author='Dotan Nahum',
    data_files=[('', ['LICENSE', 'README.md'])],
    author_email='jondotan@gmail.com',
    url='https://github.com/jondot/dotrunner',
    license=license,
    py_modules=['dotrunner'],
    entry_points='''
        [console_scripts]
        dotrunner=dotrunner:main
    ''',
    # packages=find_packages(exclude=('tests', 'docs', 'jest-pytest')),
    install_requires=[
        'toolz', 'docopt', 'networkx', 'pyyaml', 'delegator.py', 'colorama'
    ])
