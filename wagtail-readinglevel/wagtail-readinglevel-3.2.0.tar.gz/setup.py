#!/usr/bin/env python
"""
Installs a Wagtail plugin that adds reading level calculations to Draftail.
This helps content editors create content that conforms to the WCAG 2.0
"""

from setuptools import setup, find_packages

setup(name='wagtail-readinglevel',
      version='3.2.0',
      description='Wagtail plugin that adds reading level calculations to Draftail.',
      long_description='Wagtail plugin that adds reading level calculations to Draftail.',
      url='http://github.com/vixdigital/wagtail-readinglevel',
      author='VIX Digital',
      author_email='info@vix.digital',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'wagtail>=2.0',
      ],
      zip_safe=False)
