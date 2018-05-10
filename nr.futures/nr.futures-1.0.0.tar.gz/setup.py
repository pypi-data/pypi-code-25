
import setuptools

with open('requirements.txt') as fp:
  install_requires = fp.readlines()

setuptools.setup(
  name = 'nr.futures',
  version = '1.0.0',
  author = 'Niklas Rosenstein',
  author_email = 'rosensteinniklas@gmail.com',
  description = 'A convenient threading based future implementation compatible with Python 2 and 3.',
  url = 'https://github.com/NiklasRosenstein-Python/nr.futures',
  license = 'MIT',
  install_requires = install_requires,
  packages = setuptools.find_packages('src'),
  package_dir = {'': 'src'}
)
