import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tidues_tools",
    version="0.0.8",
    author="Tidues Wei",
    author_email="tidues@gmail.com",
    description="Tools for tidues",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://tidues001@bitbucket.org/tidues001/tidues_tools.git",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)

