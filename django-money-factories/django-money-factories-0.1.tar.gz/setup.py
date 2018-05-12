"""Factories for Django-Money Models"""
import os
from setuptools import setup

VERSION = (0, 1)
__version__ = '.'.join(str(i) for i in VERSION)
__license__ = 'BSD License'
__url__ = 'https://github.com/django-money/django-money-factories'
__author__ = 'Anthony Monthe (ZuluPro)'
__email__ = 'anthony.monthe@gmail.com'

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

setup(
    name='django-money-factories',
    version=__version__,
    py_modules=['djmoney_factories'],
    include_package_data=True,
    license=__license__,
    description=__doc__,
    long_description=README,
    url=__url__,
    author=__author__,
    author_email=__email__,
    install_requires=['factory_boy'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Framework :: Django',
    ],
)
