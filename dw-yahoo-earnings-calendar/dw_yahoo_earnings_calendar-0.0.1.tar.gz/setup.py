try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='dw_yahoo_earnings_calendar',
    packages=['yahoo_earnings_calendar'],
    install_requires=[
        'requests'
    ],
    version='0.0.1',
    description='Scrapes data from Yahoo! Finance earnings calendar',
    author='Daniel Wang',
    author_email='danielwpz@gmail.com',
    keywords=['stock', 'earnings', 'yahoo', 'scrape', 'finance'],
    classifiers=[],
)
