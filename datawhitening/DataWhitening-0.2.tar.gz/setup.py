from distutils.core import setup
setup(
  name = 'DataWhitening',
  packages = ['DataWhitening'], # this must be the same as the name above
  version = '0.2',
  description = 'A dicision making helper for black box algorithm library',
  author = 'Seddik Belkoura',
  author_email = 'seddik.belkoura@gmail.com',
  url = 'https://gitlab.com/SBINX/DataWhitening', # use the URL to the github repo
  download_url = 'https://github.com/SBINX/DataWhitening/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['testing', 'logging', 'example'], # arbitrary keywords
  classifiers = [],
  install_requires=['numpy','itertools','sklearn','time','sys']
)
