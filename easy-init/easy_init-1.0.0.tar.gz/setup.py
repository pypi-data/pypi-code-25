from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='easy_init',
    version='1.0.0',
    description='easy-to-use decorator for automatically generating the __init__ method',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ebrush/easy_init',
    author='Samuel Brush',
    author_email='s.e.brush1@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='metaprogramming decorators class method',
    packages=find_packages(include=['easy_init']),
    project_urls={
        'Bug Reports': 'https://github.com/ebrush/easy_init/issues',
        'Source': 'https://github.com/ebrush/easy_init',
    },
)
