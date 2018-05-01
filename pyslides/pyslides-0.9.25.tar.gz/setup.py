from setuptools import setup
from os.path import join as pjoin

setup(name='pyslides',
      version='0.9.25',
      description='Python-based tool for presentation-ready slides',
      author='Giuseppe Romano',
      author_email='romanog@mit.edu',
      classifiers=['Programming Language :: Python :: 2.7','Programming Language :: Python :: 3.6'],
      long_description=open('README.rst').read(),
      install_requires=['pybtex','matplotlib','PyPDF2','pillow','future'], 
      license='GPLv2',
      entry_points = {
     'console_scripts': [
      'download_pyslides_example=pyslides.download_pyslides_example:main'],
      },
      packages=['pyslides'],
      zip_safe=False)
