# -*- coding: UTF-8 -*-

"""
Setup for repchar
"""

from io import open
import os.path
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

long_description = u""
with open(os.path.join(here, "README.rst"), "r", encoding="UTF-8") as f:
    long_description = f.read()

version = u""
with open(os.path.join(here, "repchar", "__init__.py"), "r") as f:
    for line in f:
        if line.find("__version__") != -1:
            version = line.split("=")[1].strip()
            version = version[1:-1]
            break

setup_args = dict(
        name="repchar",
        description="Simple reporter for characters used in a file",
        version=version,
        author="Clemens Radl",
        author_email="clemens.radl@googlemail.com",
        maintainer="Clemens Radl",
        maintainer_email="clemens.radl@googlemail.com",
        url="https://github.com/rotula/repchar",
        long_description=long_description,
        license="MIT",
        install_requires=[],
        packages=find_packages(),
        entry_points={"console_scripts":
            ["repchar=repchar.scripts.repchar_script:main"],},
        keywords="unicode",
        classifiers=[
            "License :: OSI Approved :: MIT License",
            "Development Status :: 5 - Production/Stable",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.6",
            "Environment :: Console",
            "Topic :: Text Processing",
            "Topic :: Text Processing :: General",
        ]
)

setup(**setup_args)
