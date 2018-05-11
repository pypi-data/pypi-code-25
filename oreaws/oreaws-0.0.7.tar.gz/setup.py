#!/usr/bin/env python

#from setuptools import setup
from setuptools import find_packages, setup

setup(
      name='oreaws',
      version='0.0.7',
      description='Python AWS CLI Tool',
      license='MIT',
      author='yhidetoshi',
      author_email='example@python.net',
      url='https://github.com/yhidetoshi/python-awscli-tool',
      packages=['oreaws'],
#      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      install_requires=['boto3','prettytable','click'],
      py_modules=['def_ec2','def_s3','def_autoscaling','def_route53'],
      entry_points={
              'console_scripts': [
                     'oreaws = oreaws.awscli:main',
               ],
      }
)
