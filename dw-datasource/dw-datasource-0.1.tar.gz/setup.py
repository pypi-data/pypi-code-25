try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='dw-datasource',
      version='0.1',
      description='Stock related data',
      author='Daniel Wang',
      author_email='danielwpz@gmail.com',
      license='MIT',
      packages=['datasource'],
      install_requires=[
          'tiingo',
          'pandas',
          'beautifulsoup4',
          'requests',
          'quandl'
      ],
      zip_safe=False)
