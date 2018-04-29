from setuptools import setup
setup(
  name = 'specific_import',
  version = '0.8',
  description = 'This library allows users to import resources by their relative or absolute file paths',
  url = 'https://github.com/sudouser2010/specific_import',
  author = 'Herbert Dawkins',
  author_email = 'DrDawkins@ClearScienceInc.com',
  packages = ['specific_import'],
  include_package_data=True,

  keywords = ['specific', 'import', 'file'],
  python_requires='~=3.6',
  install_requires=[],

)
