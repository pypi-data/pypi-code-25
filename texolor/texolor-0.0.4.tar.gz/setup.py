import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="texolor",
    version="0.0.4",
    author="Saurabh Londhe",
    author_email="saurabhlondhe1111@gmail.com",
    description="A small colored text module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/saurabhlondhe/python-Scripts/blob/master/sau.py",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
