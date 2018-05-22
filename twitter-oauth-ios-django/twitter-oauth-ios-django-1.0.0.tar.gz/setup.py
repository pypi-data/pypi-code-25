# coding: utf-8
from setuptools import setup, find_packages

import os.path


NAME = 'twitter-oauth-ios-django'
VERSION = '1.0.0'


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    with open(filename, 'r') as f:
        return f.read()


def readlist(filename):
    rows = read(filename).split('\n')
    rows = [row.strip() for row in rows if row.strip()]
    return list(rows)


setup(
    name=NAME,
    version=VERSION,
    description='Create UserSocialAuth of social_django with OAuth login with twitter-kit-ios.',
    long_description=read('README.rst'),
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keyword='django ios twitter oauth',
    author='nnsnodnb',
    author_email='ahr63_gej@me.com',
    url='https://github.com/nnsnodnb/twitter-oauth-django',
    download_url='https://github.com/nnsnodnb/twitter-oauth-django/tarball/master',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': [
                'README.rst',
                'requirements.txt',
                'LICENSE',
            ]
    },
    zip_safe=False,
    install_requires=readlist('requirements.txt'),
)

