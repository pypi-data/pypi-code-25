from setuptools import setup

setup(name='email_scraper_from_html',
      version='1.0',
      description='Generates list of emails scraped from a given HTML file',
      url='https://github.com/jonjonrankin/email_scraper_from_html',
      author='jonjonrankin',
      author_email='jonathan@skoller.co',
      license='MIT',
      packages=['email_scraper_from_html'],
      zip_safe=False,
      install_requires=[
            'bs4',
            'pandas',
            'argparse'
      ],
      python_requires='>=3',
      scripts=['bin/scrape'])