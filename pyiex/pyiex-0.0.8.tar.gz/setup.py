from os import path
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pyiex",

    version='0.0.8',

    author="Wentao Lu",
    author_email="wentao@wentaolu.com",

    description="Python wrapper for IEX financial API",
    long_description=long_description,

    url="https://github.com/wugui2020/pyIEX",

    license="LICENSE.txt",

    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "Programming Language :: Python :: 2.7"
    ],

    keywords="python IEX",

    packages=find_packages(exclude=["docs", "tests"]),

    install_requires=[
        "http-request-randomizer==1.2.2",
    ],

    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage"],
    }
)
