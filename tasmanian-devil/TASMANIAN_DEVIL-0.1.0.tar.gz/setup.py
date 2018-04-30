import re
import os
from setuptools import setup, Extension
from codecs import open
from os import path

version_file = open("TASMANIAN_DEVIL/_version.py", "r").read()
version_match = re.match(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file)
if (version_match):
    version = version_match.group(1)
else:
    raise RuntimeError("Unable to find version string in _version.py")

here = path.abspath(path.dirname(__file__))
#Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
 
setup(name = "TASMANIAN_DEVIL",
      setup_requires=['numpy', 'scipy<1.0'],
      install_requires=['numpy', 'scipy<1.0', 'pandas', 'pycrypto', 'argparse', 'cobra==0.8.2', 'sympy', 'python-libsbml'],
      packages = ["TASMANIAN_DEVIL"],
      author="Edwin H. Gibb and Travis J. Lawrence",
      entry_points = {"console_scripts": ['tas = TASMANIAN_DEVIL.TASMANIAN_DEVIL:main']},
      version = version,
      description = "TASMANIAN DEVIL: a software package for classifying gene activity from omics data sets, simplifying metabolic networks, and visualizing the estimated phenotypic fluxes of nutrients",
      long_description=long_description,
      license='LGPLv3',
      url = "https://tlawrence3.github.io/Tasmanian-Devil",
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                   'Natural Language :: English',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.6',
                   'Topic :: Scientific/Engineering :: Bio-Informatics'],)

