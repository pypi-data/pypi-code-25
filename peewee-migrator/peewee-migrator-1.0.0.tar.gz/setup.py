# -*- coding: utf-8 -*-
import codecs
from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
with codecs.open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [x.strip() for x in f.readlines()]

setup(
    name='peewee-migrator',
    version='1.0.0',
    description='Basic migrations support for peewee ORM',
    author='Suguby',
    author_email='suguby@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    url='https://github.com/suguby/peewee-migrator',
    keywords='peewee migrations orm',
    data_files=[
        ('', ['requirements.txt', 'README.rst', ], ),
    ],
    packages=find_packages(include=['migrator']),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'migrator=migrator.cli:cli'
        ]
    }
)
