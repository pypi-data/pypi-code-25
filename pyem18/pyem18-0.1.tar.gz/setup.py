from setuptools import setup, find_packages

setup(name='pyem18',
      version='0.1',
      description='A Python library to read data from EM-18 RFID reader module',
      url='http://github.com/dhavalsavalia/pyem18',
      author='Dhaval Savalia',
      author_email='dhaval.savalia6@gmail.com',
      license='MIT',
      packages=find_packages(),
      keywords='em18 rfid reader',
      install_requires = ['pyserial'],)