# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os


version = '4.8.10001'

here = os.path.abspath(os.path.dirname(__file__))

def read_file(*pathes):
    path = os.path.join(here, *pathes)
    if os.path.isfile(path):
        with open(path, 'r') as desc_file:
            return desc_file.read()
    else:
        return ''

desc_files = (('README.rst',), ('docs', 'CHANGES.rst'),
                ('docs', 'CONTRIBUTORS.rst'))

long_description = '\n\n'.join([read_file(*pathes) for pathes in desc_files])

install_requires=['setuptools']


setup(name='openmairie.robotframework',
      version=version,
      description="RobotFramework Library for functional testing openMairie Framework based apps",
      long_description=long_description,
      platforms = ["any"],
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords="openMairie RobotFramework",
      author="openMairie",
      author_email="contact@openmairie.org",
      url="https://github.com/openmairie/openmairie.robotframework/",
      license="GPL",
      packages=find_packages("src"),
      package_dir = {"": "src"},
      namespace_packages=["openmairie"],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

# vim:set et sts=4 ts=4 tw=80:
