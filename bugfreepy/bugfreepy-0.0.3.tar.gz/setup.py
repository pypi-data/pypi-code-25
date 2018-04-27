#!/usr/bin/env python
# created by BBruceyuan on 18-4-27

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import bugfreepy

setup(
    name='bugfreepy',
    version=bugfreepy.__verison__,
    author=bugfreepy.__author__,
    author_email='bruceyuan123@gmail.com',
    url='https://github.com/hey-bruce/bugfreepy',
    description="add a text pic in your python file, but it is just for fun",
    packages=['bugfreepy', 'text_pictures'],
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'bfp=bugfreepy.main:main'
        ]
    }
)
