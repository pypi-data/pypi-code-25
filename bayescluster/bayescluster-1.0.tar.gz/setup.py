
from setuptools import setup,find_packages

setup(name = "bayescluster",
      version = "1.0",
      description='A clustering package which uses bayesian methods and returns classifications and a tree structure',
      author='Matthew Welch, Yamac Isik',
      author_email='matt.welch@duke.edu ,yamac.isik@duke.edu',
      url='https://github.com/mtw25/Stat663FinalProject-Matt_Yamac',
      license='MIT',
      py_modules = ['bayescluster'],
      packages=find_packages(),
      install_requires=['numpy','scipy'],
      python_requires='>=3',
      )