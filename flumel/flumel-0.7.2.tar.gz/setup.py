"""
Setup

Usage :
* `python setup.py test -> unittests
"""

from setuptools import setup, find_packages

try:
    from pypandoc import convert
    README = convert('README.md', 'rst')
except ImportError:
    print('!!! pandoc manquant, la description sera en markdown')
    README = open('README.md').read()

with open('requirements.in') as requirements:
    REQUIRES = requirements.read().splitlines()

setup(
    name='flumel',
    version='0.7.2',  # managed by bumbversion
    description='Encore un moyen de recevoir ses flux RSS par email',
    author='Canarduck',
    author_email='renaud@canarduck.com',
    url='https://gitlab.com/canarduck/flumel',
    keywords='rss email',
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description=README,
    entry_points={
        'console_scripts': [
            'flumel-init=flumel.cli:init',
            'flumel-page=flumel.cli:generate_page',
            'flumel-config=flumel.cli:generate_config'
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta', 'Environment :: Web Environment',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Communications :: Email',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary'
    ],
    test_suite='tests')
