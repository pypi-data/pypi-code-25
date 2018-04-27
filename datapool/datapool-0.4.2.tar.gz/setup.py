#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

readme = """EAWAG sensor data warehouse

For documentation please look at https://datapool.readthedocs.org

"""

# !!!! DO NOT FORGET TO UPDATE requirements.txt !!!!!

requirements = [
    "sqlalchemy",
    "psycopg2",
    "Click",
    "ruamel.yaml",
    "psutil",
    "watchdog",
    "pandas",
]

# !!!! DO NOT FORGET TO UPDATE requirements.txt !!!!!


setup(
    name='datapool',
    version='0.4.2',  # don't forget to update datapool/__init__.py !
    description="EAWAG data warehouse",
    long_description=readme,
    author="Uwe Schmitt",
    author_email='uwe.schmitt@id.ethz.ch',
    url='https://github.com/uweschmitt/datapool',
    packages=find_packages(exclude=["tests", "sandbox"]),
    package_dir={'datapool':
                 'datapool'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='datapool',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points='''
        [console_scripts]
        pool=datapool.main:main
                        '''
)

