# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='attics',  # Required
    version='0.0.1',  # Required
    description='Attics project TBD',  # Required
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    # url='https://github.com/pypa/sampleproject',  # Optional
	license='LICENSE.txt',
    author='Ruslan',  # Optional
    author_email='r@gmail.com',  # Optional
    # keywords='sample setuptools development',  # Optional
    packages=['attics', 'attics.generator'],  # Required
    # install_requires=['peppercorn'],  # Optional
)