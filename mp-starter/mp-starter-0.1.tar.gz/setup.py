#!/usr/bin/env python

from os import path as op

from setuptools import setup, find_packages


def _read(fname):
    try:
        return open(op.join(op.dirname(__file__), fname)).read()
    except IOError:
        return ''


install_requires = [
    l for l in _read('requirements.txt').split('\n')
    if l and not l.startswith('#')]

tests_require = [
    l for l in _read('requirements_dev.txt').split('\n')
    if l and not l.startswith('#')]

description = """mp-mp_starter is a lib to optimize my workflow when starting a project.\
Creating the project and its skeleton.\
"""

setup(
    name='mp-starter',
    version='0.1',
    license='BSD',
    description=description,
    long_description=_read('README.md'),
    keywords="mp_starter django project".split(),  # noqa
    author='Lucas Cardoso',
    author_email='mr.lucascardoso@gmail.com',
    url='https://github.com/mrlucascardoso/mp-starter',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'starter=mp_starter.cli.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Natural Language :: Portuguese',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ],
)

