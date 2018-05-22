from distutils.core import setup
import os
import subprocess

subprocess.call(['./fastent_install.sh'])


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
  name = 'fastent',
  packages = ['fastent'], # this must be the same as the name above
  version = '0.5.3',
  description = 'Automated Custom NER tool',
  author = 'Erik Arakelyan',
  author_email = 'erikarakelyan1997@gmail.com',
  install_requires=requirements,
  url = 'https://github.com/fastent/fastent', # use the URL to the github repo
  long_description=readme(),
  download_url = 'https://github.com/fastent/fastent/archive/0.5.tar.gz', # I'll explain this in a second
  keywords = ['NER', 'Anotation', 'Contextualization'], # arbitrary keywords
  classifiers = [],
)
