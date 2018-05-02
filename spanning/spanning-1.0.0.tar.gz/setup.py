from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='spanning',  # Required
    version='1.0.0',
    description='Provides reference-based access over list-like objects',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Gorea235/python-spanning',
    author='Luke (Gorea235)',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='list list-like reference large',
    packages=['spanning'],
    project_urls={
        'Bug Reports': 'https://github.com/Gorea235/python-spanning/issues',
        'Source': 'https://github.com/Gorea235/python-spanning',
    },
)
