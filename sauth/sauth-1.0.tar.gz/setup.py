#!/usr/bin/env python

from sauth import __version__, __prog__
from setuptools import setup

setup(
    name=__prog__,
    version=__version__,
    license="GNU General Public License v3",
    description='Simple Auth Server SSL',
    author='Bernardas Ališauskas',
    author_email='tinarg@protonmail.com',
    url='https://github.com/granitosaurus/sauth/',
    py_modules=['sauth'],
    install_requires=['click'],
    entry_points={
        'console_scripts': [
            'sauth=sauth:main'
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.3',
    ],
)
