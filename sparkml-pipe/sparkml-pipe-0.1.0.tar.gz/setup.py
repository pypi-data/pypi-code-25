# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

requirements = [
    "setuptools>=28.8.0",
    "numpy>=1.14.2",
    "pandas>=0.22.0",
    "pyspark>=2.3.0",
    "PyYAML>=3.12",
]

with open("sparkmlpipe/__version__.py") as fh:
    version = fh.readlines()[-1].split()[-1].strip("\"'")

setup(
    name='sparkml-pipe',
    description='A configurable pyspark pipeline.',
    version=version,
    packages=find_packages(exclude=['test']),
    install_requires=requirements,
    include_package_data=True,
    author='Feng Zhao',
    author_email='parkerzf@gmail.com',
    license='BSD',
    platforms=['Linux'],
    classifiers=[],
    url='https://bitbucket.org/xtechai/sparkml-pipe')
