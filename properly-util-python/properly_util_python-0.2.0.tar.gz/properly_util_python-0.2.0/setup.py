import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="properly_util_python",
    version="0.2.0",
    author="Tomiwa Ademidun",
    author_email="tomiwa@goproperly.com",
    description="Utility and helper functions for properly functions in python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GoProperly/properly-util-python",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
    ),
)