from setuptools import setup

setup(
  name='netmon',
  version='0.1.42',
  author='Denis Khshaba',
  author_email='deniskhoshaba@gmail.com',
  scripts=['netmon'],
  url = 'https://github.com/theden/netmon',
  keywords = ['network', 'monitor', 'linux'],
  license='LICENSE',
  description='network monitor for linux',
  long_description=open('README.md').read(),
  install_requires=[
    'ascii_graph',
    'cursor',
  ]
)
