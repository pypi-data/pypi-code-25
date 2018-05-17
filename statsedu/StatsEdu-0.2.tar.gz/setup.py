# License MIT

import os

from setuptools import setup, find_packages

from setuptools import setup


DISTRO_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))



setup(
    name='StatsEdu',
    version='0.2',
    description='Statistic package. Include functions to calculate different descriptive statistics and build plot, '
                'histogram or boxplot.',
    author='Elena Golosovskaia',
    author_email='elena.golosovskaia@gmail.com',
    url='https://pypi.org/user/Feesterra',
    license='MIT',
    classifiers=[
        'Topic :: Education',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'matplotlib==2.2.2'
        ],
    test_suite='nose.collector',
    include_package_data=True
)