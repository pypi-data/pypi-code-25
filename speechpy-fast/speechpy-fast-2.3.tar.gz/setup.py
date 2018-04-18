from setuptools import setup, find_packages

setup(name='speechpy-fast',
      version='2.3',
      description='A fork of the python package for extracting speech features.',
      author='Amirsina Torfi, Matthew Scholefield',
      author_email='matthew331199@gmail.com',
      url='https://github.com/matthewscholefield/speechpy',
      download_url = 'https://github.com/matthescholefield/speechpy/archive/2.3.zip',
      packages=find_packages(exclude=('tests', 'docs')),
      include_package_data=True,
      install_requires=[
          'scipy',
          'numpy',
          'backports.functools_lru_cache;python_version<"3.2"'
      ],
      zip_safe=False)
