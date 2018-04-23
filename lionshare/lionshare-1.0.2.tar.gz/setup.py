from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='lionshare',
    packages=['lionshare'],
    version='1.0.2',
    license='MIT',
    description='Python wrapper for the Lionshare API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Abhinav Kasamsetty',
    author_email='abhinavkasamsetty@gmail.com',
    url='https://github.com/abhinavk99/lionshare',
    keywords=['lionshare', 'cryptocurrency', 'api', 'wrapper'],
    install_requires=['requests'],
    extras_require={
        'test': ['pytest']
    }
)
