# -*- coding: utf-8 -*-


import os
from setuptools import setup

import lbn


this_dir = os.path.dirname(os.path.abspath(__file__))


with open(os.path.join(this_dir, "README.md"), "r") as f:
    long_description = f.read()

keywords = [
    "physics", "hep", "particle", "vector", "lorentz", "boost", "numpy", "tensorflow",
]

classifiers = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Development Status :: 4 - Beta",
    "Operating System :: OS Independent",
    "License :: OSI Approved :: MIT License",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Information Technology",
]

install_requires = []
with open(os.path.join(this_dir, "requirements.txt"), "r") as f:
    install_requires.extend(line.strip() for line in f.readlines() if line.strip())

setup(
    name=lbn.__name__,
    version=lbn.__version__,
    author=lbn.__author__,
    author_email=lbn.__email__,
    description=lbn.__doc__.strip(),
    license=lbn.__license__,
    url=lbn.__contact__,
    keywords=" ".join(keywords),
    classifiers=classifiers,
    long_description=long_description,
    install_requires=install_requires,
    python_requires=">=2.7",
    zip_safe=False,
    # packages=["lbn"],
    package_data={
        "": ["LICENSE", "requirements.txt", "README.md"],
    },
)
