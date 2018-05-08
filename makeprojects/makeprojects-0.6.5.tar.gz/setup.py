#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Build the egg file for makeprojects for python

Copyright 2013-2018 by Rebecca Ann Heineman becky@burgerbecky.com

It is released under an MIT Open Source license. Please see LICENSE
for license details. Yes, you can use it in a
commercial title without paying anything, just give me a credit.
Please? It's not like I'm asking you for money!

"""

from __future__ import absolute_import, print_function, unicode_literals
from setuptools import setup
import sys

#
# Project specific strings
#

projectname = 'makeprojects'
projectkeywords='makeprojects xcode visual studio visualstudio codeblocks watcom ps4 xboxone xbox360 vita mac ios android'

#
# Manually import the project
#

projectmodule = __import__(projectname)

#
# Create the dependency list
#

install_requires = [
	'setuptools >= 0.7.0',
	'enum34 >= 1.0.0',
	'burger >= 1.0.2',
	'argparse >= 1.0'
]

#
# Parms for setup
#

setup_args = dict(

	name=projectname,
	version=projectmodule.__version__,

#
# Use the readme as the long description
#

	description=projectmodule.__summary__,
	long_description=open('README.rst').read(),
	license=projectmodule.__license__,
	url=projectmodule.__uri__,

	author=projectmodule.__author__,
	author_email=projectmodule.__email__,

	keywords=projectkeywords,
	platforms='any',
	install_requires=install_requires,

	classifiers=[
		'Development Status :: 3 - Alpha',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Topic :: Software Development',
		'Topic :: Software Development :: Build Tools',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Natural Language :: English',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.0',
		'Programming Language :: Python :: 3.1',
		'Programming Language :: Python :: 3.2',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6'
	],
	packages=[projectname],

	entry_points={
		'console_scripts': [ 'makeprojects = makeprojects.__main__:main' ]
	}
)

#
# Perform the setup
#

if __name__ == '__main__':
	setup(**setup_args)
