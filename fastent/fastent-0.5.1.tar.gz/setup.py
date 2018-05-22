from distutils.core import setup
import os

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
  name = 'fastent',
  packages = ['fastent'], # this must be the same as the name above
  version = '0.5.1',
  description = 'Automated Custom NER tool',
  author = 'Erik Arakelyan',
  author_email = 'erikarakelyan1997@gmail.com',
  install_requires=requirements,
  url = 'https://github.com/fastent/fastent', # use the URL to the github repo
  long_description=read('README.md'),
  download_url = 'https://github.com/fastent/fastent/archive/0.5.tar.gz', # I'll explain this in a second
  keywords = ['NER', 'Anotation', 'Contextualization'], # arbitrary keywords
  classifiers = [],
)
