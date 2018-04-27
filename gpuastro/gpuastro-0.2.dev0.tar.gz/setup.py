#from distutils.core import setup
from setuptools import setup

setup(
    name='gpuastro',
    version='0.2dev',
    packages=['gpuastro',],
    license='GNU',
    long_description=open('README.txt').read(),
	description = 'A GPU accelerated astrophysics library',
	author = 'Gill, S.',
	author_email = 's.gill@keele.ac.uk',
	url = 'https://github.com/samgill844', # use the URL to the github repo
	keywords = ['GPU', 'numba', 'astrophysics'], # arbitrary keywords
	classifiers = [])
