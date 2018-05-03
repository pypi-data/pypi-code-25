from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    install_requires=['aiohttp'],
    name='animu-cf',
    version='0.1.0',
    description='An Python API Wrapper for CF\'s API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/CFCorp/animu.py',
    author='August (Chris)',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='hentai anime animu api api-wrapper'
)