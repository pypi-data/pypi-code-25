#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['coverage==4.5.1', 'mock==2.0.0', 'mysql-connector-python==8.0.11', 'nose==1.3.7', 'Pillow==5.1.0', ]

# setup_requirements = ['pytest-runner', ]
#
# test_requirements = ['pytest', ]

setup(
    author="Sergii Iukhymchuk",
    author_email='sergii.iukhymchuk83@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        # "Programming Language :: Python :: 2",
        # 'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        # 'Programming Language :: Python :: 3.6',
    ],
    description="GUI to manage such staff information as Time Off, Vacation, Salary and Commission changing. This data is recorded to mysql DB.",
    entry_points={
        'gui_scripts': [
            'launcher=staff_info:__main__',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='staff_info',
    name='staff_info',
    packages=find_packages(exclude=['*.db_credentials']),
    # setup_requires=setup_requirements,
    test_suite='tests',
    # tests_require=test_requirements,
    url='https://github.com/sergii.iukhymchuk83@gmail.com/staff_info',
    version='0.1.2',
    zip_safe=False,
)
