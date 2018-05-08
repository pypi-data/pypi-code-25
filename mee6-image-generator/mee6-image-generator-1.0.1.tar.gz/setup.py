from setuptools import setup, find_packages

import generator

setup(name='mee6-image-generator',
      version=generator.__version__,
      description='Image generator',
      author='Mee6 Team',
      author_email='dev@mee6bot.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'cairosvg',
          'pystache',
          'redis',
          'boto3',
      ],
      zip_safe=True)
