import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
  name = 'qspin',
  packages = find_packages(),
  version = '2.1.0',
  description = 'Learn quantum spin, entanglement, and quantum computer operations',
  long_description = read('README.rst'),
  long_description_content_type='text/x-rst',
  author = 'Don Gavel',
  author_email = 'donald.gavel@gmail.com',
  url = 'https://bitbucket.org/donald_gavel/qspin', # the github repo
  install_requires=[
    'numpy',
  ],
  download_url = 'https://bitbucket.org/donald_gavel/qspin/downloads',
  keywords = ['quantum', 'spin', 'electron','qubit','quantum computing','entanglement','entropy'], # arbitrary keywords
  classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Information Technology',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2.7',
    'Topic :: Scientific/Engineering :: Physics',
    'Operating System :: MacOS',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Unix',
    ],
)
