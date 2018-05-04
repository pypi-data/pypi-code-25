"""Setup.py for the Matils Library."""

from setuptools import setup, find_packages

setup(
    name='matils',
    version='0.1.1',
    author='Mathias Santos de Brito',
    author_email='mathias.brito@me.com',
    maintainer='Mathias Santos de Brito',
    maintainer_email='mathias.brito@me.com',
    description='Collection of utilities using only the Python Standard \
                 Library',
    url='https://github.com/mathiasbrito/matils',
    test_suit='tests',
    packages=find_packages()
)
