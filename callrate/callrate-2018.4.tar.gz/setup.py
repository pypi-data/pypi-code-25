from setuptools import setup
import os

if os.path.exists('Readme.md'):
    with open('Readme.md') as readme_file:
        long_description = readme_file.read()
else:
    long_description = 'No description'

s = setup(
    name='callrate',
    version='2018.04',
    description='Package to manage functions call rate',
    install_requires=[],
    long_description=long_description,
    license='MIT',
    author='Anton Bautkin',
    author_email='antonbautkin@gmail.com',
    url='https://gitlab.com/goblenus/requestslimitrate',
    packages=['callrate'],
    entry_points={}
)
