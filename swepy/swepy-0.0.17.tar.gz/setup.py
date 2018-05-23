import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="swepy",
    version="0.0.17",
    author="William Norris",
    author_email="wino6687@colorado.edu",
    description="A python package for obtaining and cleaning Tb files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wino6687/SWEpy",
    packages=setuptools.find_packages(),
    install_requires=[
          'affine','requests', 'nco', 'netCDF4',
          'datetime', 'tqdm', 'mapboxgl', 'pandas',
          'scikit-image'
      ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ),
)
