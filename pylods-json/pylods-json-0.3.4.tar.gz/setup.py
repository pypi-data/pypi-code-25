from setuptools import setup

setup(
  name = 'pylods-json',
  packages = ['pylodsjson'], # this must be the same as the name above
  version = '0.3.4',
  description = 'json extension for pylods msgpack',
  author = 'Salim Malakouti',
  author_email = 'salim.malakouti@gmail.com',
  license = 'MIT',
  url = 'https://github.com/salimm/pylods-ijson', # use the URL to the github repo
  download_url = 'http://github.com/salimm/pylods-json/archive/0.3.4.tar.gz', # I'll explain this in a second
  keywords = ['python','serialization','deserialization','paser','json','object oriented','fast','extendable','type based','jackson json', 'ijson'], # arbitrary keywords
  classifiers = ['Programming Language :: Python'],
  install_requires=['pylods','ijson'],
)
