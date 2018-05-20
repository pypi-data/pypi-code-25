# -*- coding: utf-8 -*-
# project-system (c) Ian Dennis Miller

import re
import os
import codecs
from setuptools import setup
from setuptools import find_packages


def read(*rnames):
    return codecs.open(os.path.join(os.path.dirname(__file__), *rnames), 'r', 'utf-8').read()


def grep(attrname):
    pattern = r"{0}\W*=\W*'([^']+)'".format(attrname)
    strval, = re.findall(pattern, read('project_system/__meta__.py'))
    return strval


setup(
    version=grep('__version__'),
    name='project-system',
    description="create and open projects",
    packages=find_packages(),
    scripts=[
        "bin/project-conf-init",
        "bin/project-git-init",
        "bin/project-list",
        "bin/project-new",
        "bin/project-new3",
        "bin/project-open",
        "bin/project-workon",
    ],
    long_description=read('Readme.rst'),
    classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    include_package_data=True,
    keywords='',
    author=grep('__author__'),
    author_email=grep('__email__'),
    url=grep('__url__'),
    install_requires=read('requirements.txt'),
    license='MIT',
    zip_safe=False,
)
