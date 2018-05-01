from setuptools import setup, find_packages

__version__ = '0.0.2'

setup(
    name='Flask-DatastoreLogger',
    version=__version__,
    description='A logging interface for Google Cloud Datastore',
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
