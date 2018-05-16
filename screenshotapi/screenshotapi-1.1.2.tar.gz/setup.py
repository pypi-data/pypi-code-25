import re
from codecs import open as codecs_open
from setuptools import setup, find_packages

# read the version number from source
version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('screenshotapi/screenshotapi.py').read(),
    re.M
    ).group(1)

# Get the long description from the relevant file
with codecs_open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(name='screenshotapi',
      version=version,
      description='Python API Client for Screenshotapi.io',
      long_description=long_description,
      keywords=['screenshot'],
      author='Doug Kerwin',
      author_email='dwkerwin@gmail.com',
      url='https://github.com/screenshotapi/screenshotapi-python',
      packages=find_packages(),
      install_requires=[
        'requests>=2.18.4, <3.0',
        'six>=1.11.0, <2.0'
      ],
      entry_points={
        "console_scripts": ['screenshotapi = screenshotapi.screenshotapi:main']
      },
      license='MIT',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        ]
     )
