# To use a consistent encoding
import codecs
import re
from os import path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))


def read(*parts):
    with codecs.open(path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Get the long description from the README file
with codecs.open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='sankeydata',
    version=find_version('src', 'sankeydata', '__init__.py'),
    description="Data structure for Sankey diagrams.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ricklupton/sankeydata',
    author='Rick Lupton',
    author_email='mail@ricklupton.name',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='Sankey diagram flow data format JSON',
    packages=find_packages('src', exclude=['docs', 'test']),
    package_dir={'': 'src'},
    install_requires=[
        'attrs',
    ],
    extras_require={
        'dev': [],
        'test': ['pytest'],
    },
)
