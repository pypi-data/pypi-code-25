#!/usr/bin/env python

import os
from setuptools import setup, find_packages
# from jpathpy import __version__

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "jpathpy",
    # version = __version__,
    version = '1.1.9',
    packages = find_packages(),
    install_requires=['ply>=3.9,<4'],
	
	exclude_package_data = {
		"": ["*.out", "*tab.py"]
	},
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.txt", "*.rst", "LICENSE"]
    },

    # metadata for upload to PyPI
    author = "Vladimir Saltykov",
    author_email = "vowatchka@mail.ru",
    description = "Package for selection JSON members from JSON by using JPath query",
	long_description = read("jpathpy\README.rst"),
    license = "MIT",
    keywords = "jpathpy python jpath json syntax member members",
    #url = "",   # project home page, if any

    # tests
	test_suite = "jpathpy.tests",
	
	# zip
	zip_safe = True,
	
	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Topic :: Utilities",
	],
)
