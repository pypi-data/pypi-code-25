from codecs import open as codecs_open
from setuptools import setup, find_packages


# Get the long description from the relevant file
with codecs_open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(name='screenshotapi',
      version='1.1',
      description='Python API Client for Screenshotapi.io',
      long_description=long_description,
      author='Doug Kerwin',
      author_email='dwkerwin@gmail.com',
      license='MIT',
      url='https://github.com/screenshotapi/screenshotapi-python',
      packages=['screenshotapi'],
      install_requires=open('requirements.txt').readlines()
     )
