#!/usr/bin/env python
from setuptools import find_packages, setup

project = "microcosm-secretsmanager"
version = "0.2.0"

setup(
    name=project,
    version=version,
    description="Secrets storage using AWS SecretsManager",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp/microcosm-secretsmanager",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "microcosm>=2.1.0",
        "boto3>=1.7.9",
    ],
    setup_requires=[
        "nose>=1.3.6",
    ],
    dependency_links=[
    ],
    entry_points={
    },
    tests_require=[
        "coverage>=3.7.1",
        "mock>=1.0.1",
        "PyHamcrest>=1.8.5",
    ],
)
