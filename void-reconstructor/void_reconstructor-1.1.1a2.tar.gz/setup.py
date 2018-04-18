from setuptools import setup

setup(
    name='void_reconstructor',    # This is the name of your PyPI-package.
    description='Tools for reconstructing the velocities in a LCDM universe using the Jonker-Volgenant algorithm',
    version='1.1.1a2',# Update the version number for new releases
    author_email = 'tobias.meier@epfl.ch',
    install_requires=['lapjv',],
    packages=['void_reconstructor'],         # The name of your scipt, and also the command you'll be using for calling it
    python_requires='>=3'
    )