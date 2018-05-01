"""Collect from Phoenix Contact SOLARCHECK String Monitor and send the data to your cloud using Ardexa

See:
https://github.com/ardexa/solarcheck-strings
"""

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='solarcheck_ardexa',
    version='1.3.0',
    description='Collect from Phoenix Contact SOLARCHECK String Monitor and send the data to your cloud using Ardexa',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ardexa/solarcheck-strings',
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

    keywords='Phoenix Contact SOLARCHECK solar string monitor ardexa',
    py_modules=['solarcheck_ardexa'],
    install_requires=[
        'future',
        'ardexaplugin',
        'Click',
    ],

    entry_points={
        'console_scripts': [
            'solarcheck_ardexa=solarcheck_ardexa:cli',
        ],
    },

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/ardexa/solarcheck-strings/issues',
        'Source': 'https://github.com/ardexa/solarcheck-strings/',
    },
)
