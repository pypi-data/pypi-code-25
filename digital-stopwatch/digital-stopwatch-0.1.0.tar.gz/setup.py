# -*- coding: utf-8 -*-
 
 
"""setup.py: setuptools control."""
 
 
import re
from setuptools import setup
 
 
version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('digital_stopwatch/digital_stopwatch.py').read(),
    re.M
    ).group(1)
 
 
with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")
 
 
setup(
    name = "digital-stopwatch",
    packages = ["digital_stopwatch"],
    entry_points = {
        "console_scripts": ['digital_stopwatch = digital_stopwatch.digital_stopwatch:main']
        },
    version = version,
    description = "A digital stopwatch made using Tk and a multithreading library",
    long_description = long_descr,
    author = "Alexei Ciobanu",
    author_email = "alexei.ciobanu95@gmail.com",
    )