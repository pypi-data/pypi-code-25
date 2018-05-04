import codecs
import os
import re

from setuptools import setup, find_packages


###################################################################

NAME = "pylistone"
PACKAGES = find_packages(exclude=[])
KEYWORDS = ["list manipulation", "lua arrays"]
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

INSTALL_REQUIRES = []

###################################################################

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()





if __name__ == "__main__":
    setup(
        name=NAME,
        description="Makes lists start at one",
        license="LICENSE",
        url="https://github.com/KuanHulio/pylistone",
        version="1.0.0",
        author="Sami Altamimi",
        author_email="nkjjsami@gmail.com",
        maintainer="Sami Altamimi",
        maintainer_email="nkjjsami@gmail.com",
        keywords=KEYWORDS,
        long_description=read("README.md"),
        packages=PACKAGES,
        zip_safe=True,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
    )