"""
PascalsTriangle
-------------

Simple script for calculating the Pascals Triangle, up to
a given depth.

You can get it by downloading it directly or by typing:

    $ pip install PascalsTriangle

After it is installed you can start it by simply typing in your terminal:

    $ pascals-triangle 'integer representing desired depth(row) of a Pascals Triangle'

"""


from setuptools import setup

setup(name='PascalsTriangle',
      version='0.1',
      description='Calculates the Pascals Triangle, up to a given depth',
      long_description=__doc__,
      long_description_content_type='text/markdown',
      url="https://github.com/urosjevremovic/PascalsTriangle",
      license='MIT',
      author='Uros Jevremovic',
      author_email='jevremovic.uros91@gmail.com',
      packages=['PascalsTriangle'],
      entry_points={
          "console_scripts": ["pascals-triangle=PascalsTriangle.pascals_triangle:main"],
      },
      )

__author__ = 'Uros Jevremovic'
