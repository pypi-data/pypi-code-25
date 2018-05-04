#!/usr/bin/env python3

from distutils.core import setup

import os


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            if not path.endswith('__pycache__') and not filename.endswith(".pyc"):
                paths.append(os.path.relpath(os.path.join(path, filename), directory))
    return paths

extra_files = package_files('xaled_utils/')

#print extra_files

setup(
      name='xaled_utils',
      version='0.8.0', # major.minor.fix: MAJOR incompatible API changes, MINOR add backwards-compatible functionality, FIX bug fixes
      description='Frequently used functions library for Python3 By Khalid Grandi (github.com/xaled).',
      long_description='Frequently used functions library for Python3 By Khalid Grandi (github.com/xaled).',
      long_description_content_type='text/x-rst',
      keywords='library utils common',
      author='Khalid Grandi',
      author_email='kh.grandi@gmail.com',
      url='https://github.com/xaled/xaled_utils/',
      install_requires=['requests', 'pycrypto', 'pyaml', 'lxml'],
      python_requires='>=3',
      packages=['xaled_utils'],
      package_data={'': extra_files},
     )
