#!/usr/bin/env python

import os
from setuptools import setup, find_packages
from rmsynthesis import __version__

scripts = [
    "rmsynthesis/bin/rmsynthesis"
]

requires = [ 
    "numpy",
    "astropy",
    "multiprocessing",
    "cleanmask"
]


setup(name="rm-synthesis",
    version=__version__,
    description="Performs Rotation Measurement(RM) Synthesis and RM Cleaning on FITS Cube Images",
    author="Lerato Sebokolodi",
    author_email="mll.sebokolodi@gmail.com",
    url="https://github.com/Sebokolodi/RMSYNTHESIS/",
    packages=find_packages(),
    requires=requires,
    scripts=scripts, 
    license="GPL2",
    classifiers=[],
 )
