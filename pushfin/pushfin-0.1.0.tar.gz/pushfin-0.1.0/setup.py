import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pushfin",
    version = "0.1.0",
    author = "Steffen Vogel",
    author_email = "post@steffenvogel.de",
    description = "Publishes bank account statements via MQTT and Pushover.",
    license = "GPL-3.0",
    keywords = "HBCI FinTS Pushover MQTT",
    url = "https://github.com/stv0g/pushfin",
    long_description = read('README.md'),
    scripts=[
	    'bin/pushfin'
    ],
    install_requires = [
	'pyyaml',
	'fints'
    ],
    zip_safe = False,
    classifiers = [
	"Development Status :: 5 - Production/Stable",
	"Programming Language :: Python :: 3.6",
	"Programming Language :: Python :: 3.7",
	"Topic :: Office/Business :: Financial",
	"Topic :: Home Automation",
	"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
    ]
)
