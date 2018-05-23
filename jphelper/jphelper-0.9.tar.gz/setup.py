from setuptools import setup, find_packages
import unittest
import os.path


def get_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('jphelper.tests', pattern='test_*.py')
    return test_suite


with open('README.rst', encoding='utf-8') as f:
    long_desc = f.read()


setup(
    name='jphelper',
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),
    version='0.9',
    description='A collection of japanese text and number manipulation tools.',
    author='Michael Devara',
    author_email='michael.devara@gmail.com',
    test_suite='setup.get_test_suite',
    keywords=['japanese', 'utility', 'utils', 'tools'],
    license='MIT',
    platforms=['any'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Environment :: Other Environment',
        'Natural Language :: Japanese',
        'Operating System :: OS Independent',
        'Topic :: Utilities'
    ],
    url='https://github.com/michaeldvr/jphelper',
    long_description=long_desc,
    long_description_content_type='text/markdown; charset=UTF-8; variant=GFM',
    python_requires='>=3'
)
