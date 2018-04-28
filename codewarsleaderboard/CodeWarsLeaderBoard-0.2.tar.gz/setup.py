"""
CodeWarsLeaderBoard
-------------

Script that runs a web scraper in a background for getting
leader board details for 500 top users of codewars.com

You can get it by downloading it directly or by typing:

    $ pip install CodeWarsLeaderBoard

After it is installed you can start it by simply typing in your terminal:

    $ code-wars-leader-board


"""


from setuptools import setup

setup(name='CodeWarsLeaderBoard',
      version='0.2',
      description='Runs a web scraper in a background for getting leader '
                  'board details for 500 top users of codewars.com',
      long_description=__doc__,
      long_description_content_type='text/markdown',
      url="https://github.com/urosjevremovic/CodeWarsLeaderBoard",
      license='MIT',
      author='Uros Jevremovic',
      author_email='jevremovic.uros91@gmail.com',
      packages=['CodeWarsLeaderBoard'],
      install_requires=['bs4', 'requests', ],
      entry_points={
          "console_scripts": ["code-wars-leader-board=CodeWarsLeaderBoard.codewars_leaderboard:main"],
      },
      )

__author__ = 'Uros Jevremovic'
