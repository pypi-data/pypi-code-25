#!/usr/bin/env python

from setuptools import setup
from pip.req import parse_requirements


install_reqs = parse_requirements('requirements.txt', session='hack')
reqs = [str(ir.req) for ir in install_reqs]

setup(name='amazon-ses-template-editor',
      version='0.3',
      description='A tool for editing, uploading and testing Amazon SES email templates',
      author='Andrii Kostenko',
      author_email='andrii@short.cm',
      scripts=['amazon-ses-template-editor.py'],
      install_requires=reqs
     )
