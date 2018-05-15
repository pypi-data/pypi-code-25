# Always prefer setuptools over distutils
# To use a consistent encoding
from codecs import open
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(

    name='satori-serpentarium',
    version='0.0.2a3',
    description='Satori composer for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://bitbucket.addsrv.com/users/yzhuk/repos/serpentarium/browse',
    packages=find_packages(exclude=['docs', 'tests*']),
    package_data={
        'serpentarium': ['config.yml'],
    },
    install_requires=[
        'datadog',
        'networkx',
        'wsaccel',
        'PyYAML',
        'retrying',
        'pydot',
        'graphviz',
        'argparse',
        'satori-rtm-sdk'
    ],
    python_requires='>=3.6.5',
)
