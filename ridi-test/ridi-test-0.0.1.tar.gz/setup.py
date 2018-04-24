"""A setuptools based setup module.
"""

from setuptools import setup, find_packages

setup(
    name='ridi-test',
    packages=[
        'ridi.test',
    ],
    version='0.0.1',
    description='Ridi TEST',
    url='https://github.com/ridi/cms-sdk',
    keywords=['ridi', 'ridibooks'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'thrift>=0.10.0',
        'requests>=2.0.0',
    ],
)
