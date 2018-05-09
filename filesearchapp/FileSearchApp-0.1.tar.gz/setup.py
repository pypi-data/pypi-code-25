"""
File search app
-------------

Script for checking folder and all of its sub-folders
for occurrence of a given string in all of its files.

You can get it by downloading it directly or by typing:

    $ pip install FileSearchApp

After it is installed you can run it from CLI:

    $ file_search

Output will be printed in a terminal windows, along with total number of
occurrences and saved in a .csv file for easier browsing of results.

"""


from setuptools import setup

setup(name='FileSearchApp',
      version='0.1',
      description="Script for checking folder and all of its sub-folders for occurrence of a given string in all of "
                  "its files.",
      long_description=__doc__,
      long_description_content_type='text/markdown',
      url="https://github.com/urosjevremovic/File-Search-App",
      license='MIT',
      author='Uros Jevremovic',
      author_email='jevremovic.uros91@gmail.com',
      packages=['FileSearchApp'],
      entry_points={
          "console_scripts": ["file_search=FileSearchApp.file_search_app:main", ],
      },
      )

__author__ = 'Uros Jevremovic'
