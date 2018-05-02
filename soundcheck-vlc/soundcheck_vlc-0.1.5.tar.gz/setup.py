# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='soundcheck_vlc',
    version='0.1.5',
    description='Turns maston toots into a vlc playlist',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='alfajet',
    author_email='alfajet@protonmail.com',
    url='https://framagit.org/alfajet/soundcheck-vlc',
    license=license,
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Sound/Audio',

        # Pick your license as you wish
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
        ],
    keywords='mastodon vlc sound audio',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'appdirs>=1.4.0',
        'Mastodon.py>=1.2.2',
        'requests>=2.18.0',
    ],

    entry_points={
        'console_scripts': ['soundcheck-vlc=soundcheck_vlc.cli:run'],
    },
    project_urls={
        'Bug Reports': 'https://framagit.org/alfajet/soundcheck-vlc/issues',
        'Source': 'https://framagit.org/alfajet/soundcheck-vlc/',
        'Mastodon': 'https://mastodon.xyz/tags/soundcheckvlc',
},    
)

