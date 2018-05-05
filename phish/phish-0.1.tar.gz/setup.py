from setuptools import setup, find_packages


setup(
  name = 'phish',
  packages = ['phish'], # this must be the same as the name above
  version = '0.1',
  description = 'A library to easily access the phish.net api',
  author = 'Remington Stone',
  author_email = 'remstone7@gmail.com',
  url = '', # use the URL to the github repo
  keywords = ['testing', 'logging', 'phish'], # arbitrary keywords
  license='MIT',
  classifiers = [],
  install_requires=['requests']
)
