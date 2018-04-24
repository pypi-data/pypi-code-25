from __future__ import division, print_function

import io
import os
import re

from setuptools import setup

long_description = """
==========
frp nat for pyhton
==========
"""
if os.name == "nt":
    scripts = None
    entry_points = {
        'console_scripts': [
            'frp.py=frp:_main',
            'frps.py=frps:_main',
            'frpc.py=frpc:_main',
        ],
    }
else:
    scripts = ['frp.py',
               'frps.py',
               'frpc.py']
    entry_points = None

setup(
    name='frpd',
    py_modules=['frp', 'frps', 'frpc'],
    version='0.0.2',
    description='frp NAT.',
    long_description=long_description,
    url='https://github.com/nat-cloud/frp',
    author='Farry',
    author_email='yu@iotserv.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: Embedded Systems',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    tests_require=[],
    install_requires=[],
    scripts=scripts,
    entry_points=entry_points,
)