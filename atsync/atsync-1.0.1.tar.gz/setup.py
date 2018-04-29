"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='atsync',
    version='1.0.1',
    description='One way sync python dicts to airtable.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://bitbucket.org/mckinnonsc-ericv/atsync/',
    author='Eric van de Paverd | McKinnon Secondary College',
    author_email='ericv@mckinnonsc.vic.edu.au',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Database',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='airtable etl database sync',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['airtable-python-wrapper'],
    project_urls={
        'Bug Reports': 'https://bitbucket.org/mckinnonsc-ericv/atsync/issues/',
        'Source': 'https://bitbucket.org/mckinnonsc-ericv/atsync/src/',
    },
)
