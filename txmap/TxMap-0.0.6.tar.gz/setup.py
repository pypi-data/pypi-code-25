import codecs
import os
import sys

try:
	from setuptools import setup, find_packages
except:
	from distutils.core import setup

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "TxMap",
    version = "0.0.6",
    description = "A hepler tools for tencent map api",
    long_description = read("README.txt"),
    classifiers =
	[
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
		'Topic :: Scientific/Engineering :: Astronomy',
		'Topic :: Scientific/Engineering :: GIS',
		'Topic :: Scientific/Engineering :: Mathematics',
		'Intended Audience :: Science/Research',
		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
    ],
    keywords = "Tencent Map Tools",
    author = "blackcat",
    author_email = "kfx2007@163.com",
    url ="https://github.com/block-cat/txmap",
    license = "GNU",
    packages = find_packages(),
    include_package_data= True,
    zip_safe= True,
)