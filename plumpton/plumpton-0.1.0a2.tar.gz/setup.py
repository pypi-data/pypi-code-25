from setuptools import setup
from codecs import open
from os import path

import plumpton

# Get current path.
dir = path.abspath(path.dirname(__file__))

# Open readme in current path.
with open(path.join(dir, 'README.md'), encoding='utf-8') as file:

    # Store readme file in variable.
    readme = file.read()

# Execute setup method.
setup(
    name = 'plumpton',
    version = plumpton.PLUMPTON_VERSION,
    description = 'A Python text-based game library.',
    long_description = readme,
    long_description_content_type = 'text/markdown',
    url = 'https://thomaswoodcock.net/plumpton',
    author = "Thomas Woodcock",
    author_email = "thomas@thomaswoodcock.net",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Education',
        'Topic :: Games/Entertainment',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Tcl Extensions',
    ],
    project_urls = {
    'Source': 'https://github.com/thomaswoodcock/plumpton'
    },
    py_modules = ['plumpton'],
)
