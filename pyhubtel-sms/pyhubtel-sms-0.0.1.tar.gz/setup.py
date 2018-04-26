#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from codecs import open
from shutil import rmtree

from setuptools import Command, setup

here = os.path.abspath(os.path.dirname(__file__))

packages = ["pyhubtel_sms"]

requires = [
    "requests>=2.18.4", "phonenumberslite>=8.9.1", "python-dateutil>=2.7.0"
]

about = {}
with open(
    os.path.join(here, "pyhubtel_sms", "__version__.py"), "r", "utf-8"
) as f:
    exec(f.read(), about)

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


class Publish(Command):
    """Publish to PyPI and Github"""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        print("\033[1m{}\033[0m\n".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system(
            "{} setup.py sdist bdist_wheel --universal".format(sys.executable)
        )

        self.status("Uploading the package to PyPI via Twine…")
        # https://github.com/productml/blurr/pull/130
        os.system("twine upload dist/*.gz")
        os.system("twine upload dist/*.whl")

        self.status("Pushing git tags…")
        os.system("git tag v{}".format(about["__version__"]))
        os.system("git push --tags")

        sys.exit()


setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=about["__url__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    keywords="hubtel sms development",
    packages=packages,
    package_dir={"pyhubtel_sms": "pyhubtel_sms"},
    include_package_data=True,
    install_requires=requires,
    python_requires=">=2.6, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    license=about["__license__"],
    cmdclass={"publish": Publish},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
