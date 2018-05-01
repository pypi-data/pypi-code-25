import os

from setuptools import setup

py_modules = ['bot', 'skeleton']
setup(name='silbacre',
      version='0.1.8',
      description='Silence (SMSSecure) backup file API',
      author='Ralph Embree',
      author_email='ralph.embree@brominator.org',
      url='https://gitlab.com/ralphembree/silbacre',
      #packages=['silbacre'],
      install_requires=['bs4', 'phonenumbers', 'strudel'],
      scripts=['silbacre'],
)
