from setuptools import setup

setup(name='fmqlutils',
      description = 'FMQL Utilities',
      long_description = """A Python framework and set of executables for caching datasets from FileMan systems using FMQL. Includes support for data analysis and modeling""",
      version='2.0',
      classifiers = ["Development Status :: 4 - Beta"],
      url='http://github.com/Caregraf/FMQL/fmqlutils',
      license='Apache License, Version 2.0',
      keywords='VistA,FileMan,CHCS,MongoDB,FMQL',
      package_dir = {'fmqlutils': ''},
      packages = ['fmqlutils', 'fmqlutils.cacher', 'fmqlutils.transformers', 'fmqlutils.fmqlIF', 'fmqlutils.schema', 'fmqlutils.reporters'],
      entry_points = {
          'console_scripts': ['cacher=fmqlutils.cacher.cacher:main']
      }
)
