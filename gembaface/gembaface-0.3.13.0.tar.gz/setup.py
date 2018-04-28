import os
from setuptools import setup


VERSION = '0.3.13.0'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='gembaface',
    version=VERSION,
    description="Simple client for GembaFace services",
    packages=['gembaface'],
    install_requires=[
        'requests',
        ],
    use_2to3=True
    )
    
