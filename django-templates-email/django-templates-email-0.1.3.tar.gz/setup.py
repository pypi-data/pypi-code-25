#!/usr/bin/env python
from setuptools import setup

setup(
    name='django-templates-email',
    version='0.1.3',
    description='',
    long_description='',
    author='Nicholas Wolff',
    author_email='nwolff@gmail.com',
    url='https://github.com/skioo/django-templates-email',
    packages=[
        'templates_email',
    ],
    install_requires=[
        'Django>=1.11',
        'structlog',
        'typing',
        'django-render-block',
        'premailer',
        'lxml',
    ],
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
    ],
)
