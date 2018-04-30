# Imports
import setuptools as settool
import os

# Define Important Project-wide Data
release = "0.1-A1"
name = "FrozenDesert"


# Read Files
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# Variables
scriptList = []

settool.setup(
    name=name,
    version=release,
    packages=settool.find_packages(),
    py_modules=scriptList,
    License='MIT',
    python_requires='>=3',
    # Gets the README & other related data

    package_data={
        '': ['*.rst', '*.txt']
    },

    # METADATA
    author="Zachary // 2VeryIcey",
    author_email="2veryicey@gmail.com",
    description="Frozen Desert is a small Text-Adventure With 10 classes & 3 storylines, allowing for much variety.",
    long_description=read('README.rst'),
    keywords='game text adventure fun small simple story storyline frozen desert oregon trail kingdom loathing',
    classifier=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: General Public',
        'Topic :: Game :: Text Adventure',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ]
)
