
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jmeterWebReport",
    version="0.0.1",
    author="mark",
    author_email="mamian521@gmail.com",
    description="Display JMeter HTML report",
    long_description="More convenient to show JMeter's web page report",
    long_description_content_type="text/markdown",
    url="https://github.com/magaofei/jmeterWebReport",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)