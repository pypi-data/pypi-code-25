#!/usr/bin/env python3

from setuptools import setup, find_packages


description = """A library to do mass Pagure pull requests."""

with open('README.rst') as readme:
    long_description = readme.read()

setup(
    name='mass-pagure-prs',
    version='0.1.dev1',
    description=description,
    long_description=long_description,
    keywords='pagure mass pr',
    author='Iryna Shcherbina',
    author_email='shcherbina.iryna@gmail.com',
    url='',
    license='MIT',
    packages=find_packages(),
    install_requires=['libpagure', 'selenium'],
    setup_requires=['setuptools'],
    tests_require=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
    ]
)
