"""
Setup.py for jenkins-bitbucket-build-reporter
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='bitbucket-jenkins-build-reporter',
    version='0.0.2',
    description='Post build statuses from Jenkins jobs to Bitbucket Cloud',
    long_description='A CLI to update build status for commits in Bitbucket Cloud from Jenkins',
    url='https://github.com/danielwhatmuff/bb-build-reporter',
    author='Daniel Whatmuff',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='bitbucket git jenkins build statue',
    py_modules=["bb-build-reporter"],
    install_requires=['requests', 'gitpython'],
    scripts=['bin/bb-report'],
)
