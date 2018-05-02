from setuptools import setup, find_packages
import unittest


def test_suite():
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    return suite


setup(name='Cryptolite',
      version='0.0.1',
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
      )
