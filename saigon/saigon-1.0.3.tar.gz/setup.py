# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from saigon import VERSION

setup(
    name = 'saigon',
    version = VERSION.replace(' ', '-'),
    description = 'Some useful tool for faster and more efficient AngularJs & SCSS application development.',
    author = 'Integree Bussines Solutions',
    author_email = 'dev@integree.eu',
    url = 'https://github.com/integree/saigon',
    download_url = 'https://pypi.python.org/packages/source/i/saigon/saigon-%s.zip' % VERSION,
    keywords = 'saigon angularjs scss integree',
    packages = find_packages(),
    include_package_data = True,
    license = 'MIT License',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires = [
        'django-appconf',
    ],
    zip_safe = False)
