from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='RoboWFuzz',
    version='1.0',
    packages=[''],
    package_dir={'': 'robowfuzz'},
    url='',
    license='MIT',
    author='Abhay Bhargav',
    install_requires = ['wfuzz','robotframework'],
    description='RoboWFuzz - Generic Robot Framework Library for the WFuzz Fuzzing Framework. Currently, only a Directory Bruter',
    long_description = long_description,
    long_description_content_type='text/markdown'
)
