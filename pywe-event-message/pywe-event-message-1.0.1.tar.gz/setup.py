# -*- coding: utf-8 -*-

from setuptools import setup


version = '1.0.1'


setup(
    name='pywe-event-message',
    version=version,
    keywords='Wechat Weixin Event Message',
    description='Wechat Event Message Module for Python.',
    long_description=open('README.rst').read(),

    url='https://github.com/sdkwe/pywe-event-message',

    author='Hackathon',
    author_email='kimi.huang@brightcells.com',

    packages=['pywe_event_message'],
    py_modules=[],
    install_requires=['pywe_utils', 'six', 'xmltodict'],

    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
