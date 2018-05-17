#!/usr/bin/python3 -S
import os
import uuid
from setuptools import setup, Extension
from pkgutil import walk_packages


pathname = os.path.dirname(os.path.realpath(__file__))


PKG = 'cargo_phone_number'
PKG_NAME = 'cargo-phone-number-field'
PKG_VERSION = '0.1.0'


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return (line for line in lineiter if line and not line.startswith("#"))

install_reqs = parse_requirements(pathname + "/requirements.txt")


def find_packages(prefix=""):
    path = [prefix]
    yield prefix
    prefix = prefix + "."
    for _, name, ispkg in walk_packages(path, prefix):
        if ispkg:
            yield name

setup(
    name=PKG_NAME,
    version=PKG_VERSION,
    description='A phone number field type for Cargo ORM.',
    author='Jared Lunde',
    author_email='jared.lunde@gmail.com',
    url='https://github.com/jaredlunde/cargo_phone_number',
    license="MIT",
    install_requires=list(install_reqs),
    packages=list(find_packages(PKG))
)
