from setuptools import setup


try:
    long_description = open("README.md").read()
except IOError:
    long_description = ""


setup(name='DowPy',
      version='0.1.4',
      description='Module for downloading HTTP(s) files efficiently',
      url='http://github.com/jhnbrunelle/dowpy',
      author='JohnBrunelle',
      author_email='devjohnb@gmail.com',
      license='MIT',
      packages=['dowpy'],
      long_description=long_description,
      install_requires=['requests'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)