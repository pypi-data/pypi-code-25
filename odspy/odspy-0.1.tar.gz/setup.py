from distutils.core import setup
setup(
  name = 'odspy',
  packages = ['odspy'], # this must be the same as the name above
  version = '0.1',
  description = 'LibreOffice spreadsheet parsing library',
  author = 'Stefan Nožinić',
  author_email = 'stefan@lugons.org',
  url = 'https://github.com/fantastic001/odspy', 
  download_url = 'https://github.com/fantastic001/odspy/tarball/0.1', 
  keywords = ["libreoffice", "spreadsheet"],
  package_dir = {'odspy': 'src'},
  classifiers = [],
)
