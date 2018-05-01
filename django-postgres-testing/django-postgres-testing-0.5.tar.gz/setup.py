#!/usr/bin/env python
from setuptools import setup

setup_requires = []

install_requires = [
    "django>=1.7",
]

setup(
    author='Chris Sinchok',
    author_email='chris@sinchok.com',
    name='django-postgres-testing',
    version='0.5',
    url='https://github.com/sinchok/django-postgres-testing',
    py_modules=['django_postgres_testing'],
    install_requires=install_requires,
)
