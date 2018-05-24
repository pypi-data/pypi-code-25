import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="numpycnn",
    version="1.7",
    author="Ahmed F. Gad",
    author_email="ahmed.f.gad@gmail.com",
    description="Building CNN from Scratch using NumPy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ahmedfgad/NumPyCNN",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
