"""
RealEstateAppRealitica
-------------

Script that runs a web scraper in a background and gets
all available real estates in Balkan area, and filters them
by given parameters(country, city, municipality).


You can get it by downloading it directly or by typing:

    $ pip install RealEstateAppRealitica

After it is installed you can start it by simply typing in your terminal:

    $ realitica_real_estate

Results will be printed in terminal window, and saved into CSV
file for easier browsing.

"""


from setuptools import setup

setup(name='RealEstateAppRealitica',
      version='0.1',
      description='Script that runs a web scraper in a background and gets all available real estates in Balkan area, '
                  'and filters them by given parameters(country, city, municipality).',
      long_description=__doc__,
      long_description_content_type='text/markdown',
      url="https://github.com/urosjevremovic/Real-estate-app",
      license='MIT',
      author='Uros Jevremovic',
      author_email='jevremovic.uros91@gmail.com',
      packages=['RealEstateApp'],
      install_requires=['bs4', 'requests'],
      entry_points={
          "console_scripts": ["realitica_real_estate=RealEstateApp.real_estate_app_2:main"],
      },
      )

__author__ = 'Uros Jevremovic'
