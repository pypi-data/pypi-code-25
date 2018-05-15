#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
	name="Scratch_Analysis_Tool",
	version="1.0.2",
	author="XiaoLing Chai",
	author_email="347920697@qq.com",
	description="Scratch Analysis Tool(SAT)",
	long_description="Scratch Analysis Tool(SAT)",
	license="MIT",
	url="https://github.com/BUPT902-Scratch/ScratchAnalysis",
	packages=['Scratch_Analysis_Tool'],
	install_requires=[
		"antlr4-python2-runtime ; python_version<='2.7'",
		"antlr4-python3-runtime ; python_version>'3.3'",
	],
	entry_points={
		'console_scripts': [
			'SAT=SAT.Gen:gen',
		],
	},
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Environment :: Console",
		"Intended Audience :: Developers",
		"Operating System :: OS Independent",
		"Topic :: Education",
		"Topic :: Education :: Computer Aided Instruction (CAI)",
		"Topic :: Education :: Testing",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6"
		],
	)
