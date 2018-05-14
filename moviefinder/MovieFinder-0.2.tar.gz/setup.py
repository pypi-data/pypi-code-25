"""
MovieFinder
-------------

Script for finding movies by given term.
It will get all the movies from database that contain a given term
and print them out along with the year they were released. Results
will be printed in chronological order, from newer to older.
There will also be a folder with the same name as input term that will contain
posters of all movies that were found, if available.

You can get it by downloading it directly or by typing:

.. code:: bash

    $ pip install MovieFinder

After it is installed you can start it by simply typing in your terminal:

.. code:: bash

    $ movie_finder

"""


from setuptools import setup

setup(name='MovieFinder',
      version='0.2',
      description='Script for finding movies by given term. It will get all the movies from database that contain a '
                  'given term and print them out along with the year they were released. Results will be printed in '
                  'chronological order, from newer to older. There will also be a folder with the same name as input '
                  'term that will contain posters of all movies that were found, if available.',
      long_description=__doc__,
      long_description_content_type='text/markdown',
      url="https://github.com/urosjevremovic/Movie-Searcher",
      license='MIT',
      author='Uros Jevremovic',
      author_email='jevremovic.uros91@gmail.com',
      packages=['MovieSearcher'],
      install_requires=['requests'],
      entry_points={
          "console_scripts": ["movie_finder=MovieSearcher.movie_searcher:main"],
      },
      )

__author__ = 'Uros Jevremovic'
