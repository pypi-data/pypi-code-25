from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='amet',
    version='0.4',

    packages=['amet'],

    description='A library to read complex configuration from environment variables.',
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Mauro de Carvalho',
    author_email='mauro.dec@gmail.com',

    url='https://github.com/maurodec/amet',
    download_url='https://github.com/maurodec/amet/archive/0.4.tar.gz',

    project_urls={
        'Source': 'https://github.com/maurodec/amet',
        'Bug Reports': 'https://github.com/maurodec/amet/issues'
    },

    keywords='confiuration configuration-management environment environment-variables heroku',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'License :: OSI Approved :: MIT License',

        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',

        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',

        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration'
    ],
)
