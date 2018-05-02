from setuptools import setup, find_packages
import os
import unittest


def test_suite():
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    return suite


def readme():
    """
    Utility function to read the README file.
    Used for the long_description.  It's nice, because now 1) we have a top level
    README file and 2) it's easier to type in the README file than to put a raw
    string in below.
    :return: The contents of `README.md`
    """
    return open(os.path.join(os.path.dirname(__file__), "README.md")).read()


setup(name='Cryptolite',
      version='0.0.3',
      description='Simple, "right" cryptography.',
      author='David Carboni',
      author_email='david@carboni.io',
      classifiers=[
          'Development Status :: 1 - Planning',
          'Programming Language :: Python :: 3.2',
          'Topic :: Security :: Cryptography',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
      ],
      keywords=['cryptography', 'encryption', 'digital signature', 'key generation', 'key management'],
      url='https://github.com/davidcarboni/cryptolite/tree/python',
      license='MIT',
      packages=find_packages(),
      test_suite='setup.test_suite',
      include_package_data=True,
      zip_safe=True,
      long_description=readme(),
      long_description_content_type="text/markdown",
      )
