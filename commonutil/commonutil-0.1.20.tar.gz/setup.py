#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup  # pylint: disable=import-error

setup(
		name="commonutil",
		version="0.1.20",  # REV-CONSTANT:rev 5d022db7d38f580a850cd995e26a6c2f
		url="https://bitbucket.org/cheyinl/commonutil-py",
		description="Common utility functions",
		packages=[
				"commonutil",
				"commonutil.net",
				"commonutil.tool",
				"commonutil.tool.templatemarker",
				"commonutil.tool.vcshelper",
		],
		package_dir={
				"": "lib",
		},
		classifiers=[
				"Development Status :: 5 - Production/Stable",
				"Intended Audience :: Developers",
				"License :: OSI Approved :: MIT License",
				"Operating System :: POSIX",
				"Programming Language :: Python :: 2.7",
		],
		license="MIT License",
)

# vim: ts=4 sw=4 ai nowrap
