#!/usr/bin/env python
"""
Setupfile for pdftools.

:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2018-04-14 20:40:27
:last modified by:   Stefan Lehmann
:last modified time: 2018-05-04 14:14:01

"""
import io
import os
import ast
import re
from setuptools import setup


# Regular expression for the version
_version_re = re.compile(r'__version__\s+=\s+(.*)')


def read_file(*names, **kwargs):
    """Return content of the given file."""
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()


def extract_version():
    """Extract the version from the package."""
    with open('pdftools/__init__.py', 'r') as f:
        content = f.read()

    version_match = _version_re.search(content)
    version = str(ast.literal_eval(version_match.group(1)))
    return version


# Add long description from Markdown file
try:
    long_description = read_file('README.md')
except FileNotFoundError:
    long_description = ''


setup(
    name='pdftools',
    version=extract_version(),
    packages=['pdftools'],
    scripts=['pdfsplit.py', 'pdfmerge.py', 'pdfrotate.py', 'pdfzip.py',
             'pdfinsert.py', 'pdfremove.py', 'pdfadd.py', 'pdfcopy.py'],
    url='https://github.com/MrLeeh/pdftools',
    license='MIT',
    author='Stefan Lehmann',
    author_email='Stefan.St.Lehmann@gmail.com',
    description='A collection of convenience scripts for pdf manipulation, '
                'based on the PyPdf2 package.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['PyPdf2'],
    maintainer='Stefan Lehmann',
)
