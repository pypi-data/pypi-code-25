
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
 
    name='yibanApi',  # Required


    version='0.0.13',  # Required


    description='愉快调用yiban Api',  # Required

    long_description=long_description,  # Optional


    long_description_content_type='markdown',  # Optional (see note above)

    url='https://github.com/awefight/yibanApi',  # Optional

   
    author='The Python Packaging Authority',  # Optional

    author_email='pypa-dev@googlegroups.com',  # Optional

    classifiers=[  # Optional


        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],


    keywords='愉快调用yiban Api',  # Optional


    packages=find_packages(exclude=['requests']),  # Required

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/awefight/yibanApi/issues',
        'Source': 'https://github.com/awefight/yibanApi/',
    },
)