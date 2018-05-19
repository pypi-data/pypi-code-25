# -*- coding: utf-8 -*-

from codecs import open
from os import path

from setuptools import setup


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), 'r', encoding='utf-8') as fp:
    long_description = fp.read()


setup(
    name='slack_log_utils',
    version='0.1.0',
    description='A Python logging handler for Slack integration',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Logging'
    ],
    keywords='logging slack slack-webhook',
    url='https://github.com/ngafid/slack-log-utils',
    author='KeltonKarboviak',
    author_email='kelton.karboviak@gmail.com',
    license='MIT',
    packages=['slack_log_utils'],
    install_requires=[
        'requests>=2.18.0',
    ],
    extras_require={
        'test': ['nose'],
    },
    include_package_data=True,
    zip_safe=False,
    project_urls={
        'Source': 'https://github.com/ngafid/slack-log-utils/',
        'Say Thanks!': 'https://saythanks.io/to/KeltonKarboviak',
    },
    # test_suite='nose.collector',
    # tests_require=['nose'],
)
