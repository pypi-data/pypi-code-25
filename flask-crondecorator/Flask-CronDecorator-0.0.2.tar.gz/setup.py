import os
from setuptools import setup, find_packages

__version__ = '0.0.2'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='Flask-CronDecorator',
    version=__version__,
    description='Securely decorates Google Cloud Cron Endpoints via convention and X-Appengine-Cron header',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/MobiusWorksLLC/Flask-CronDecorator.git',
    author='Tyson Holub',
    author_email='tholub@mobiusworks.com',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'Flask'
    ]
)
