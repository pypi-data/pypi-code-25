from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

try:
    import pypandoc
    long_description = pypandoc.convert(path.join(here, 'README.md'), 'rst')
except(IOError, ImportError):
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

setup(name='itermplot',
      packages=find_packages(),
      install_requires=[
        'matplotlib',
        'six',
        'numpy'
      ],
      version='0.32',
      description='An awesome iTerm2 backend for Matplotlib, so you can plot directly in your terminal.',
      long_description=long_description,
      url='http://github.com/daleroberts/itermplot',
      author='Dale Roberts',
      author_email='dale.o.roberts@gmail.com',
      license='MIT',
      zip_safe=False)
