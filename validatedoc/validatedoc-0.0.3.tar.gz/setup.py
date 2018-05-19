"""setup.py."""
from codecs import open
from os import path

from setuptools import find_packages
from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_desc = f.read()

setup(
    name="validatedoc",
    version="0.0.3",
    packages=find_packages(exclude=['docs', 'tests']),
    license="MIT",
    author="Matthew Bentley",
    author_email="matthew@bentley.link",
    description="Do some doc string validateion",
    long_description=long_desc,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'validatedoc = validatedoc.validatedoc:main',
        ],
    },
    install_requires=[],
    python_requires='>=3.5',
)
