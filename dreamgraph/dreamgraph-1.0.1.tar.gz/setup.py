from distutils.core import setup
with open('README.md', 'r') as f:
  description = f.read()
setup(
  name = 'dreamgraph',
  packages = ['dreamgraph'],
  version = '1.0.1',
  long_description = description,
  long_description_content_type="text/html",
  description = 'The Python module for Telegraph API',
  author = 'Jasur Nurboev',
  author_email = 'bluestacks6523@gmail.com',
  url = 'https://github.com/JasurbekNURBOYEV/DreamGraph',
  download_url = 'https://github.com/JasurbekNURBOYEV/DreamGraph/archive/1.0.0.tar.gz',
  keywords = ['telegraph', 'telegraph-api', 'python-module', 'dreamgraph'],
  classifiers = [],
)
