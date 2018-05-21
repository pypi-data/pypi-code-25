from setuptools import setup, find_packages
from sphinx.setup_command import BuildDoc
from dvina import __version__


setup(name='Dvina',
      version=__version__,
      packages=find_packages(exclude=(['tests', 'tests.*'])),
      cmdclass={'build_sphinx': BuildDoc},
      description='Dvina Active Labeling library',
      install_requires=['numpy', 'future', 'scipy', 'sklearn'],
      tests_require=['mock', 'pytest'],
      )

