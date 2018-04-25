from distutils.core import setup
long_description = "# PyPI Description Test \n\n This release just had the description as a string"

setup(
  name = 'pypi_description_test',
  packages = ['pypi_description_test'], # this must be the same as the name above
  version = '0.1',
  description = 'py_description_test',
  long_description = long_description,
  long_description_content_type = "text/markdown",
  author = 'David Vitale',
  keywords = [],
  classifiers = [],
)
