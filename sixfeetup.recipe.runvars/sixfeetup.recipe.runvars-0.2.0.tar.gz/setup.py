from setuptools import setup, find_packages
from codecs import open
from os import path

version = '0.2.0'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sixfeetup.recipe.runvars',
    description="Buildout recipe to define variables from external commands.",
    long_description=long_description,
    version=version,
    license='BSD',
    zip_safe=True,
    py_modules=['sixfeetup.recipe.runvars'],
    packages=find_packages(),
    entry_points={'zc.buildout': ['default=sixfeetup.recipe.runvars:Recipe']},
    install_requires=[
        'setuptools',
        'zc.buildout',
    ],
    author='Glenn Franxman',
    author_email='glenn@sixfeetup.com',
    url='https://github.com/sixfeetup/sixfeetup.recipe.runvars',
    keywords='runvars recipe',
    classifiers=[
        "Framework :: Buildout",
        "Framework :: Buildout :: Recipe",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
    ],
)
