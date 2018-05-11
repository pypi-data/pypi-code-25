#!/usr/bin/env python

#from setuptools import setup
from setuptools import find_packages, setup

setup(
      name='oreaws',
      version='0.0.6',
      description='Python AWS CLI Tool',
      license='MIT',
      author='yhidetoshi',
      author_email='example@python.net',
      url='https://github.com/yhidetoshi/python-awscli-tool',
      packages=['oreaws'],
#      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      install_requires=['boto3','prettytable','click'],
      py_modules=['oreaws.Modules.def_ec2','oreaws.Modules.def_s3','oreaws.Modules.def_autoscaling','oreaws.Modules.def_route53'],
      entry_points={
              'console_scripts': [
                     'oreaws = oreaws.awscli:main',
               ],
      }
)
