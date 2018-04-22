from setuptools import setup
setup(
  name = 'javasaur',
  packages = ['javasaur'], # this must be the same as the name above
  version = '0.1.1',
  description = 'Pure python library for Java code analysis',
  author = 'Thiyagaraj T',
  author_email = 'tstream.h@outlook.com',
  url = 'https://github.com/tstreamDOTh/javasaur', # use the URL to the github repo
  download_url = 'https://github.com/tstreamDOTh/javasaur/archive/0.1.1.tar.gz', # I'll explain this in a second
  keywords = ['java', 'javalang', 'javaparser', 'parser'], # arbitrary keywords
   install_requires=[
          'javalang',
      ],
)