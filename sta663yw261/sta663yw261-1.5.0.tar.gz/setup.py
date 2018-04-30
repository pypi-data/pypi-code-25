import setuptools
from setuptools import setup

setup(name = "sta663yw261",
      version = "1.5.0",
      description='Sta663 Final Project',
      author='Yixuan Wang',
      license='MIT',
      author_email='yixuan.wang@duke.edu',
      url='https://github.com/wyx951029',
      py_modules = ['sta663yw261'],
      packages=setuptools.find_packages(),
      scripts = ['run_sta663.py'],
      python_requires='>=3',
      )