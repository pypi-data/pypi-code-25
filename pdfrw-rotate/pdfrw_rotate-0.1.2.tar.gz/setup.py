from distutils.core import setup

setup(
  name = 'pdfrw_rotate',
  packages = ['pdfrw_rotate'], # this must be the same as the name above
  version = '0.1.2',
  description = 'Executable to rotate all pages in a PDF document',
  long_description = 'This script uses the pdfrw library to perform a specified rotation on each page of the PDF docment.',
  author = 'Naive Roboticist',
  author_email = 'naiveroboticist@gmail.com',
  license = 'MIT',
  url = 'https://github.com/naiveroboticist/pdfrw_rotate',
  download_url = 'https://github.com/naiveroboticist/pdfrw_rotate/archive/0.1.tar.gz',
  keywords = ['pdfrw', 'rotate', 'pdf'],
  scripts=['bin/pdfrw_rotate.py'],
  classifiers = [],
)
