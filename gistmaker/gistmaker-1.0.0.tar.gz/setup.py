from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='gistmaker',

    version='1.0.0',

    description='An extremely simple python module used to programatically create Gists',

    long_description=long_description,

    long_description_content_type='text/markdown', 

    url='https://github.com/brandonsturgeon/gistmaker',
    author='Brandon Sturgeon',

    author_email='brandon@brandonsturgeon.com',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Code Generators'
    ],

    keywords='gist maker automatic http requests',

    py_modules=["gistmaker/gistmaker"],

    install_requires=['requests'],

    project_urls={
        'Bug Reports': 'https://github.com/brandonsturgeon/gistmaker/issues',
        'Source': 'https://github.com/brandonsturgeon/gistmaker/'
    },
)
