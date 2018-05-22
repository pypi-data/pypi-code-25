import os
from io import open
import hashlib
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

requires = [
    "click",
]

def get_algorithms_available():
    if hasattr(hashlib, "algorithms_available"):
        methods = list(hashlib.algorithms_available)
        methods.sort()
        return methods
    else:
        return ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]

console_scripts = []
for method in get_algorithms_available():
    console_scripts.append("{method} = hashtools:main".format(method=method))

setup(
    name="hashtools",
    version="0.1.0",
    description="Hash tools collection, like md5, sha1, sha256 and many other hash tools.",
    long_description=long_description,
    url="https://github.com/appstore-zencore/hashtools",
    author="zencore",
    author_email="dobetter@zencore.cn",
    license="MIT",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords=['hashtools'],
    requires=requires,
    install_requires=requires,
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=['hashtools'],
    entry_points={
        'console_scripts': console_scripts
    },
)