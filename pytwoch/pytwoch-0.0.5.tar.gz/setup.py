import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytwoch",
    version="0.0.5",
    author="TheUnravelGhoul",
    author_email="densmorgon@gmail.com",
    description="A simple Python wrapper for 2ch.hk API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheUnravelGhoul/py2ch",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        "requests",
    ],
)
