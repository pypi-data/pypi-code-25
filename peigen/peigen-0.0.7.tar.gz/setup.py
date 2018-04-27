import os
from setuptools import setup

# Eigen version - peigen version
__version__ = '0.0.7'

packages = []
for root, dirs, files in os.walk('.'):
    if not root.startswith('./build') and '__init__.py' in files:
        packages.append(root[2:])

data_files = []
for root, dirs, files in os.walk("include"):
    root_files = [os.path.join(root, i) for i in files]
    data_files.append((root, root_files))

setup(
  name = 'peigen',
  packages = packages,
  version = __version__,
  description = 'Python wrapper for Eigen C++ header',
  author = 'Fred Moolekamp',
  author_email = 'fred.moolekamp@gmail.com',
  url = 'https://github.com/fred3m/peigen',
  keywords = ['eigen', 'numerical'],
  data_files=data_files,
)