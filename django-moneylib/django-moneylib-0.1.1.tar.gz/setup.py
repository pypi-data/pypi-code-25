# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

setup(
    name="django-moneylib",
    version=__import__('django_money').__version__,
    description=open(os.path.join(os.path.dirname(__file__), "DESCRIPTION")).read(),
    license="The MIT License (MIT)",
    keywords="django, money, django-money, moneylib, currency",

    author="Alexander Yudkin",
    author_email="san4ezy@gmail.com",

    maintainer="Alexander Yudkin",
    maintainer_email="san4ezy@gmail.com",

    url="https://github.com/san4ezy/django-moneylib",
    packages=find_packages(exclude=[]),
    install_requires=[],
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
