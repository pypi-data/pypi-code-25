from distutils.core import setup
from setuptools import find_packages

setup(
    name='supercell-tools',
    version='0.0.1',
    packages=['hyperion','supportbot','github_helper','aws_helper'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    author="Super Cell",
    author_email="SprintTeamSuperCell@capitalone.com",
    long_description=open('README.txt').read()
)
