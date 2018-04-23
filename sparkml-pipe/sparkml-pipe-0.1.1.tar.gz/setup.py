# -*- encoding: utf-8 -*-
import os
from setuptools import setup, find_packages

requirements = [
    "pyspark>=2.3.0",
    "PyYAML>=3.12",
]


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


with open("sparkmlpipe/__version__.py") as fh:
    version = fh.readlines()[-1].split()[-1].strip("\"'")

setup(
    name='sparkml-pipe',
    description='A configurable PySpark pipeline library.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    version=version,
    packages=find_packages(exclude=['test']),
    install_requires=requirements,
    include_package_data=True,
    author='Michi Tech',
    author_email='parkerzf@gmail.com',
    license='BSD',
    platforms=['Linux'],
    classifiers=[],
    url='https://bitbucket.org/xtechai/sparkml-pipe')
