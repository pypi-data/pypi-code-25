#!/usr/bin/env python3

from setuptools import setup

setup(
    name='deep-teaching-tools',
    version='0.3',
    description='This Python module is part of the deep.TEACHING project and provides CLI tools to work with Jupyter '
                'notebooks and teaching materials.',
    author='Christoph Jansen',
    author_email='Christoph.Jansen@htw-berlin.de',
    url='https://gitlab.com/deep.TEACHING/deep-teaching-tools',
    packages=[
        'deep_teaching_tools',
        'deep_teaching_tools.stripskip'
    ],
    entry_points={
        'console_scripts': ['dtt=deep_teaching_tools.main:main']
    },
    license='MIT',
    platforms=['any'],
    install_requires=[
        'nbformat'
    ]
)
