from setuptools import setup
from os.path import join as pjoin

setup(name='pyslides',
      version='0.9.2',
      description='Tool for making slides',
      author='Giuseppe Romano',
      author_email='romanog@mit.edu',
      classifiers=['Programming Language :: Python :: 2.7'],
      long_description=open('README.rst').read(),
      install_requires=['pybtex'], 
      license='GPLv2',
      packages=['pyslides'],
      zip_safe=False)
