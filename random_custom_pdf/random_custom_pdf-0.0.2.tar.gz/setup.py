# -*- coding: utf-8 -*-
from setuptools import setup


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


setup(
    name="random_custom_pdf",
    description='numpy based random generator with custom probability '
    'distribution function',
    version="0.0.2",
    author="Vasiliy Chernov",
    author_email='kapot65@gmail.com',
    url='https://github.com/kapot65/random_custom_pdf',
    download_url='https://github.com/kapot65/random_custom_pdf/tarball/0.0.1'
    'master.zip',
    packages=["random_custom_pdf"],
    platforms='any',
    install_requires=parse_requirements("random_custom_pdf/requirements.txt")
)
