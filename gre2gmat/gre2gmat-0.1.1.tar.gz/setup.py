from distutils.core import setup
setup(
  name = 'gre2gmat',
  packages = ['gre2gmat'], # this must be the same as the name above
  version = '0.1.1',
  description = 'A library for calculating GMAT equivalent scores from GRE scores',
  author = 'Olutosin Sonuyi',
  author_email = 'tosin.sonuyi+gre2gmat@gmail.com',
  url = 'https://github.com/weallwegot/gre_to_gmat', # use the URL to the github repo
  download_url = 'https://github.com/weallwegot/gre_to_gmat/archive/0.1.1.tar.gz', 
  package_data ={'':['data_table.csv']} ,
  include_package_data=True,
  keywords = ['GMAT', 'GRE', 'Conversion', 'MBA', 'GMAC', 'ETS'], 
  classifiers = [],
)