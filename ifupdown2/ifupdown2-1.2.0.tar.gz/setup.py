#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'argcomplete',
    'ipaddr',
]

setup_requirements = [] #['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author='Roopa Prabhu',
    author_email='roopa@cumulusnetworks.com',
    maintainer="Julien Fortin",
    maintainer_email='julien@cumulusnetworks.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration'
    ],
    description="interface network manager",
    install_requires=requirements,
    license="GNU General Public License v2",
    long_description=readme,
    include_package_data=True,
    keywords='ifupdown2',
    name='ifupdown2',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/CumulusNetworks/ifupdown2',
    version='1.2.0',
    zip_safe=False,
    data_files=[
        ('/etc/default/', ['etc/default/networking']),
        ('/etc/network/ifupdown2/', ['etc/network/ifupdown2/ifupdown2.conf']),
        ('/etc/network/ifupdown2/', ['etc/network/ifupdown2/addons.conf']),
    ],
    scripts=[
        'ifupdown2/sbin/start-networking'
    ],
    entry_points={
        'console_scripts': [
            'ifup = ifupdown2.__main__:main',
            'ifdown = ifupdown2.__main__:main',
            'ifquery = ifupdown2.__main__:main',
            'ifreload = ifupdown2.__main__:main',
        ],
    }
)
