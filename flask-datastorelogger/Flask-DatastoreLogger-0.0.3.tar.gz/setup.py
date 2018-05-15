import os
from setuptools import setup, find_packages

__version__ = '0.0.3'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='Flask-DatastoreLogger',
    version=__version__,
    description='A logging interface for Google Cloud Datastore',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/MobiusWorksLLC/Flask-DatastoreLogger',
    author='Tyson Holub',
    author_email='tholub@mobiusworks.com',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'Flask',
        'google-cloud-datastore',
    ]
)
