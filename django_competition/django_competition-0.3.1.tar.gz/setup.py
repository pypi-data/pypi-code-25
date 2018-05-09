# coding=utf-8

from setuptools import find_packages, setup
import pathlib

MAIN_DIR = pathlib.Path(__file__).absolute().parent

packages = find_packages(
  str(MAIN_DIR),
  include=('django_competition',),
  exclude=[]
)

if __name__ == "__main__":

  setup(
    name='django_competition',
    version='0.3.1',
    packages=packages,
    license='Apache',
    author='Jacek Bzdak',
    author_email='jacek@askesis.pl',
    description='Simple vote mechanism for a competition',
    install_requires=[
      "Django",
      "Markdown",
      "mailchecker",
      "bleach",
    ],
    include_package_data=True
  )
