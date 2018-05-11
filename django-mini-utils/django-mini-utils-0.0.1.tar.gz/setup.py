# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

import re
import os
import sys

from setuptools import setup


package = 'djangoutils'

requirements = [
    'Django>=1.5',
    'django-discover-runner',
    'six',
]
test_requirements = [
    'model-mommy==1.3.1',
    'mock'
]


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


# python setup.py register
if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    args = {'version': get_version(package)}
    print("You probably want to also tag the version now:")
    print("  git tag -a %(version)s -m 'version %(version)s'" % args)
    print("  git push --tags")
    sys.exit()


setup(
    name='django-mini-utils',
    version=get_version(package),
    url='https://github.com/rensg001/django-utils',
    license='MIT',
    description='A django app for common utils.',
    author='ren shan gui',
    author_email='renshangui@sina.com',
    packages=get_packages(package),
    install_requires=requirements,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'
    ],
    test_suite='djangoutils.tests',
    tests_require=test_requirements
)
