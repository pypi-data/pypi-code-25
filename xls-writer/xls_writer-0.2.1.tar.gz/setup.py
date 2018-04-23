# coding=utf-8

from setuptools import find_packages, setup
import pathlib
import os

MAIN_DIR = pathlib.Path(__file__).absolute().parent


# Did I mention that setup.py is not finest piece of software on earth.
# For this to work when installed you'll need to enumerate all template and static file.


def read_dir(package: str, directory: str):
  package_root = os.path.abspath(package.replace(".", "/"))
  directory = os.path.join(package_root, directory)
  res = []
  for root, subFolders, files in os.walk(directory):
    for file in files:
      res.append(
        os.path.relpath(
         os.path.join(root, file),
         package_root
        ))

  return res


packages = find_packages(
  str(MAIN_DIR),
  include=('xls_writer*',),
  exclude=[]
)


if __name__ == "__main__":

  setup(
    name='xls_writer',
    version='0.2.1',
    packages=packages,
    license='All Rights reserved',
    author='Jacek Bzdak',
    author_email='jacek@askesis.pl',
    description='A simple utility to format tabular data from python objects.',
    install_requires=[],
    package_data={
      package: [] +
        read_dir(package, "static") +
        read_dir(package, "templates")
      for package in packages
    },
    include_package_data=True
  )
