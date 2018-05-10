"""
BelgradeRealEstateAppAdventisrealestate
-------------

Script that runs a web scraper in a background and gets
all available real estates in Belgrade, and filters them
by given parameters.


You can get it by downloading it directly or by typing:

    $ pip install BelgradeRealEstateAppAdventisrealestate

After it is installed you can start it by simply typing in your terminal:

    $ belgrade_real_estates_adventis

Results will be printed in terminal window, and saved into CSV
file for easier browsing.

"""


from setuptools import setup

setup(name='BelgradeRealEstateAppAdventisrealestate',
      version='0.7',
      description='Script that runs a web scraper in a background and gets all available real estates in Belgrade, '
                  'and filters them by given parameters.',
      long_description=__doc__,
      long_description_content_type='text/markdown',
      url="https://github.com/urosjevremovic/Belgrade-real-estate-app-adventisrealestate",
      license='MIT',
      author='Uros Jevremovic',
      author_email='jevremovic.uros91@gmail.com',
      packages=['RealEstateApp'],
      install_requires=['bs4', 'requests'],
      entry_points={
          "console_scripts": ["belgrade_real_estates_adventis=RealEstateApp.real_estate_app:main"],
      },
      )

__author__ = 'Uros Jevremovic'
