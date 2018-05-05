from setuptools import setup
from setuptools import find_packages

setup(name='pythonRestfulNews',
      version='0.5',
      description='Python Module to use RestfulNews',
      url='https://github.com/restfulnews/pythonRestfulNews',
      author='dolko',
      author_email='oliver.dolk@live.com.au',
      license='MIT',
      install_requires = [
            'requests'
      ],
      packages=find_packages(),
      zip_safe=False)