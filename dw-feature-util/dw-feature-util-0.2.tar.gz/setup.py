try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(name='dw-feature-util',
      version='0.2',
      description='Stock feature producers',
      author='Daniel Wang',
      author_email='danielwpz@gmail.com',
      license='MIT',
      packages=['feature_util'],
      install_requires=[
          'dw-datasource',
          'pandas',
          'numpy'
      ],
      zip_safe=False)
