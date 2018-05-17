from setuptools import setup, find_packages
import os
import sys

version = '0.3'

INSTALL_REQUIRES = [
        'wishbone',
]

ENTRY_POINTS = {
        'wishbone_external.function.template': [
            'uptime = test_wishbone.uptime:Uptime'
        ],
        'wishbone_external.function.module': [
            'grandtotal = test_wishbone.grandtotal:GrandTotal'
        ]
}

setup(name='test_wishbone',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='',
      author_email='',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=INSTALL_REQUIRES,
      entry_points=ENTRY_POINTS,
      )
