# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from codecs import open
from os import path

with open(path.join(path.abspath(path.dirname(__file__)),
          'README.rst'), encoding="utf-8") as f:
    long_description=f.read()

setup(
    name="pybfilter",
    version="0.1",
    packages=find_packages(),
    install_requires=["bitstring>=3.1.5"],
    description="python3 Bloom Filter",
    long_description=long_description,


    author="Zhi Sun",
    author_email="zhi.suun@gmail.com",

    python_requires='>=3',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ],
    keywords="Bloom Filter",
    url="https://github.com/imagecser/pybfilter"
)