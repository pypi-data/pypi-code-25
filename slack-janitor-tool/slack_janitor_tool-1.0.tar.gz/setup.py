#!/usr/bin/env python3

from setuptools import setup

setup(name='slack_janitor_tool',
      version='1.0',
      python_requires='>3.5.0',
      description='Your stubborn Slack Cleaning tool',
      author='Paraita Wohler',
      author_email='paraita.wohler@gmail.com',
      url='https://github.com/paraita/slack-janitor',
      packages=['slack_janitor'],
      entry_points= {
        'console_scripts': ['slack_janitor=slack_janitor.main:main'],
      }
     )
