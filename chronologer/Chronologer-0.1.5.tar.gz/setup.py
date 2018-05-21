from setuptools import setup, find_packages, findall


setup(
  name                 = 'Chronologer',
  version              = '0.1.5',
  author               = 'saaj',
  author_email         = 'mail@saaj.me',
  test_suite           = 'chronologer.test',
  license              = 'GPL-3.0',
  url                  = 'https://bitbucket.org/saaj/chronologer/src/backend',
  description          = 'Python HTTP logging server',
  long_description     = open('README.rst').read(),
  platforms            = ['Any'],
  packages             = find_packages(),
  package_data         = {'': findall('chronologer/static')},
  include_package_data = True,
  classifiers          = [
    'Topic :: Database',
    'Framework :: CherryPy',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: Implementation :: CPython',
    'Intended Audience :: Developers'
  ],
  install_requires = [
    'cherrypy < 9',
    'clor < 0.3',
    'yoyo-migrations < 6',
    'pytz'
  ],
  extras_require = {
    'mysql' : ['mysqlclient < 1.4']
  },
)

