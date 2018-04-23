# -*- coding: utf-8 -*-

from setuptools import setup


version = '1.0.2'


setup(
    name='pywe-message-reply',
    version=version,
    keywords='Wechat Weixin Message Reply',
    description='Wechat Message Reply Module for Python.',
    long_description=open('README.rst').read(),

    url='https://github.com/sdkwe/pywe-message-reply',

    author='Hackathon',
    author_email='kimi.huang@brightcells.com',

    packages=['pywe_message_reply'],
    py_modules=[],
    install_requires=['TimeConvert', 'pywe-xml>=1.0.6'],

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
