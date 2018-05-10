
import setuptools

setuptools.setup(
  name = 'nr.types',
  version = '1.0.0',
  author = 'Niklas Rosenstein',
  author_email = 'rosensteinniklas@gmail.com',
  description = 'Better named tuples, sumtypes and useful map types.',
  url = 'https://github.com/NiklasRosenstein-Python/nr.types',
  license = 'MIT',
  packages = setuptools.find_packages('src'),
  package_dir = {'': 'src'}
)
