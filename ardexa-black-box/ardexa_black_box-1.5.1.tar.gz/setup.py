"""Regularly check key Linux health items and report to a log file"""

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ardexa_black_box',
    version='1.5.1',
    description='Regularly check key Linux health items and report to a log file',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ardexa Pty Limited',
    author_email='support@ardexa.com',
    python_requires='>=2.7',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='ardexa',
    py_modules=['ardexa_black_box'],
    install_requires=[
        'dnspython',
        'future',
        'psutil',
        'requests',
    ],

    entry_points={
        'console_scripts': [
            'ardexa_black_box=ardexa_black_box:cli',
        ],
    },
)
