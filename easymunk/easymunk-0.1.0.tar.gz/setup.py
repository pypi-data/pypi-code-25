import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easymunk",
    version="0.1.0",
    author="Andrew M. Hogan",
    author_email="drewthedruid@gmail.com",
    description="An easy, versatile interface and processing handler for the munkres module.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Andrew-Hogan/easymunk",
    packages=setuptools.find_packages(),
    install_requires=['munkres'],
    platforms=['any'],
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Utilities",
    ],
)
