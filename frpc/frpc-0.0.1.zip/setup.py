# -*- coding: utf-8 -*-
from distutils.core import setup

PACKAGE = "frpc"
NAME = "frpc"
DESCRIPTION = "frp NAT Client"
AUTHOR = "Farry"
AUTHOR_EMAIL = "yu@iotserv.com"
URL = "https://github.com/nat-cloud/frpc"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    # long_description=read("README.md"),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="MIT",
    url=URL,
    packages=["frpc"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    zip_safe=False,
)
