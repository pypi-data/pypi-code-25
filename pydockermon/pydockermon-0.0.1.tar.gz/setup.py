import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="pydockermon",
    version="0.0.1",
    author="Joakim Sorensen",
    author_email="joasoe@gmail.com",
    description="A python module to interact with ha-dockermon.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ludeeus/pydockermon",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)