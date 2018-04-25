from distutils.core import setup
long_description = "# PyPI Description Test\n\nThis release changed the markdown string"

setup(
  name = 'pypi_description_test',
  packages = ['pypi_description_test'], # this must be the same as the name above
  version = '0.2',
  description = 'py_description_test',
  long_description = long_description,
  long_description_content_type = "text/markdown",
  author = 'David Vitale',
  keywords = [],
  classifiers = [],
)
