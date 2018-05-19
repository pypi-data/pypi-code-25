from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(

    name='aaafootball',  # Required

    version='0.0.0',  # Required

    description='A sample data pipeline',  # Required

    long_description=long_description,  # Optional

    long_description_content_type='text/markdown',  # Optional

    url='https://github.com/endremborza/weekndfbl',  # Optional

    author='Endre Mark Borza',  # Optional

    author_email='endremborza@gmail.com',  # Optional

    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required

    install_requires=['html5lib','pandas','matplotlib','requests','beautifulsoup4'],  # Optional

)
