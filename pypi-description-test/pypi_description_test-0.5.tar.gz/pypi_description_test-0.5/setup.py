from distutils.core import setup

#Read the description.md file
description_md_file = open("pypi_long_description.md", "r")
long_description = description_md_file.read()
description_md_file.close()


setup(
  name = 'pypi_description_test',
  packages = ['pypi_description_test'], # this must be the same as the name above
  version = '0.5',
  description = 'py_description_test',
  long_description = long_description,
  long_description_content_type = "text/markdown",
  author = 'David Vitale',
  keywords = [],
  classifiers = [],
)
