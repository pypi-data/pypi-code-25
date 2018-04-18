"""
PascalsTriangle
-------------

Simple script for calculating the Pascals Triangle, up to
a given depth.

You can get it by downloading it directly or by typing:

    $ pip install PascalsTriangle

After it is installed you can start it by simply typing in your terminal:

    $ pascals-triangle 'integer representing desired depth(row) of a Pascals Triangle'

After the script is run result will be saved in text file 'Pascals Triangle.txt'
for later reference, beside being printed in the terminal.

"""


from setuptools import setup

setup(name='PascalsTriangle',
      version='0.2',
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
