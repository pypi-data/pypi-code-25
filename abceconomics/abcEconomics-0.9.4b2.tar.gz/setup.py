
import os
import platform
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

cmdclass = {}
ext_modules = []

install_requires = ['networkx >= 1.9.1',
                    'flexx >= 0.4.1',
                    'future',
                    'dataset == 0.8']


readthedocs = os.environ.get('READTHEDOCS') == 'True'

if not readthedocs:
    if not platform.python_implementation() == "PyPy":
        install_requires += ['numpy >= 1.10.2p',
                             'pandas >= 0.17.1',
                             'bokeh']


version = '0.9.4b2'


setup(name='abcEconomics',
      version=version,
      author='Davoud Taghawi-Nejad',
      author_email='Davoud@Taghawi-Nejad.de',
      description='Agent-Based Complete Economy modelling platform',
      url='https://github.com/AB-CE/abce.git',
      package_dir={'abce': 'abce',
                   'abce.gui': 'abce/gui',
                   'abce.agents': 'abce/agents',
                   'abce.contracts': 'abce/contracts'},
      packages=['abce'],
      long_description=open('README.rst').read(),
      install_requires=install_requires,
      include_package_data=True,
      ext_modules=ext_modules,
      use_2to3=True,
      cmdclass=cmdclass)
