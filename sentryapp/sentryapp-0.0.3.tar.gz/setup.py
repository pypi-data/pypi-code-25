#/usr/bin/env python
# coding: utf8
from setuptools import setup, find_packages
from sentry_app import version

setup(
    name='sentryapp',
    version=version,
    description='server client for Sentry.app',
    author='Hepochen',
    author_email='hepochen@gmail.com',
    url='https://sentry.app',
    include_package_data=True,
    packages=find_packages(),

    install_requires = [
        'psutil'
    ],

    entry_points={
        'console_scripts':[
            'sentry_app_status = sentry_app.console:main',
        ]
    },

    platforms = 'linux',
)