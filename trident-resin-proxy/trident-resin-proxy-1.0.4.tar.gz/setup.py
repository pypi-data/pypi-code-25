# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    
    name='trident-resin-proxy',

    version='1.0.4',
    description='Python REST API that acts as a proxy to the Resin Supervisor API and Resin Data API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/openrov/trident-resin-proxy',
    author='OpenROV',
    author_email='charles@openrov.com',
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        # Supported Python Versions
        'Programming Language :: Python :: 3',
    ],

    packages=['trident-resin-proxy'],
    install_requires=['flask', 'requests', 'clidye'],
)
