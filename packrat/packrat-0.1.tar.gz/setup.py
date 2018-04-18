from __future__ import unicode_literals

from setuptools import setup, find_packages

setup(
    name='packrat',
    description=(
        'A server and Django storage backend for files you already have.'
    ),
    url='https://github.com/morganwahl/packrat',
    author='Morgan Wahl',
    author_email='morgan.wahl@gmail.com',
    license='GPLv3',
    version='0.1',
    packages=find_packages(),
    # TODO Use 'console_scripts' entry point instead.
    scripts=(
        'bin/packrat-daemon',
        'bin/packrat-update',
    ),
    install_requires=['django', 'gunicorn'],
)
