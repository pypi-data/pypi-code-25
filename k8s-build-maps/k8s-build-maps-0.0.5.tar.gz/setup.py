#!/usr/bin/env python

import os.path
import sys

import setuptools

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

setuptools.setup(
    name="k8s-build-maps",
    version="0.0.5",
    description="Build a directory of Kubernetes ConfigMap/Secret manifests, inserting data from files.",
    long_description=open(os.path.join(os.path.dirname(__file__), "README.rst")).read(),
    author="Nathan Reynolds",
    author_email="email@nreynolds.co.uk",
    url="https://github.com/nathforge/k8s-build-maps",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    install_requires=["ruamel.yaml"],
    entry_points = {
        "console_scripts": [
            "k8s-build-maps = k8s_build_maps.__main__:main",                  
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6"
    ]
)
