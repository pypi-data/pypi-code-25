from distutils.core import setup
from setuptools import find_packages

setup(
    name='supercell-slack',
    version='0.0.3',
    packages=['support_bot'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    author="Scott Snyder",
    author_email="scott.snyder@capitalone.com",
    long_description=open('README.txt').read()
)
