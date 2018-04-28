#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name="dotTest",
      packages=find_packages(),
      version="0.1",
      description="Set up .test domains for local development",
      author="Jonathan Scott",
      author_email="jonathan@jscott.me",
      url="https://github.com/jscott1989/dottest",
      download_url="https://github.com/jscott1989/dottest/archive/0.1.tar.gz",
      keywords=["local", "test"],
      scripts=["dottest"],
      install_requires=[
        "docopt>=0.6.2",
        "sh>=1.12.14",
        "pyyaml>=3.12"
      ]
      )
