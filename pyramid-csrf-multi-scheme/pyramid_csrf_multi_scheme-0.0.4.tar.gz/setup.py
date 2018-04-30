##############################################################################
#
# Copyright (c) 2017 Jonathan Vanasco and Contributors
# Portions Copyright (c) 2008-2013 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################
import os

from setuptools import setup
from setuptools import find_packages

# store version in the init.py
import re
with open(
        os.path.join(
            os.path.dirname(__file__),
            'pyramid_csrf_multi_scheme', '__init__.py')) as v_file:
    VERSION = re.compile(
        r".*__VERSION__ = '(.*?)'",
        re.S).match(v_file.read()).group(1)

try:
    here = os.path.abspath(os.path.dirname(__file__))
    README = open(os.path.join(here, "README.md")).read()
    README = README.split("\n\n", 1)[0] + "\n"
except:
    README = ''

requires = [
    "pyramid",
]

setup(
    name="pyramid_csrf_multi_scheme",
    version=VERSION,
    description="provides for creating independent csrf tokens for the http and https schemes",
    long_description=README,
    classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Pyramid",
        "Programming Language :: Python",
        "License :: Repoze Public License",
    ],
    keywords="web pyramid csrf",
    packages=['pyramid_csrf_multi_scheme',
              'pyramid_csrf_multi_scheme.tests',
              ],
    author="Jonathan Vanasco",
    author_email="jonathan@findmeon.com",
    url="https://github.com/jvanasco/pyramid_csrf_multi_scheme",
    license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
    include_package_data=True,
    zip_safe=False,
    tests_require = requires,
    install_requires = requires,
    test_suite="pyramid_csrf_multi_scheme.tests",
)
