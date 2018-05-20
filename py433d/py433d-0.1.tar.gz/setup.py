from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read()

setup(
    name='py433d',
    version=0.1,
    author='Arnaud Coomans',
    author_email='arnaud.coomans@gmail.com',
    description='A server for 433MHz (and 315Mhz) communication.',
    long_description=long_description,
    url='https://github.com/acoomans/py433',
    license='BSD',
    keywords=[
        'rpi',
        'raspberry',
        'raspberry pi',
        'rf',
        'gpio',
        'radio',
        '433',
        '433mhz',
        '315',
        '315mhz',
        'server'
    ],
    install_requires=requirements,
    scripts=['scripts/433c.py', 'scripts/433d.py'],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    package_data={'py433d': ['433d.conf']},
    include_package_data=True,
)
