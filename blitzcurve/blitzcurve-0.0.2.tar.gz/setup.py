from setuptools import setup, find_packages

from os import path

# grab the long_description from the readme file
# I'm not using unicode due to a possible distutils incompatibility. Readme cannot contain non-ASCII text.
here = path.abspath(path.dirname(__file__))
with open(path.join(here, "readme.rst")) as f:
    long_description = f.read()

setup(
    name="blitzcurve",
    author="Mark Teese and Philipp Heckmeier",
    author_email="mark.teese@checkmytumhomepage.de",
    description="Time-resolved fluorescence anisotropy analysis.",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url="https://github.com/teese/blitzcurve",
    download_url='https://github.com/teese/blitzcurve/archive/0.0.2.tar.gz',
    license='MIT',
    classifiers=['Programming Language :: Python :: 3.6',
               'License :: OSI Approved :: MIT License',
               'Intended Audience :: Science/Research',
               'Topic :: Scientific/Engineering :: Chemistry',
               'Topic :: Scientific/Engineering :: Physics',
               ],
    install_requires=["pandas", "numpy", "scipy", "matplotlib"],
    project_urls={'LangoschLab': 'http://cbp.wzw.tum.de/index.php?id=9', "TU_Munich": "https://www.tum.de"},
    keywords="fluorescence FRET rotation curve savitzky golay anisotropy time resolved TRAM single molecule protein bioinformatics biophysics microscopy",
    packages=find_packages(),
    version = "0.0.2",
    )