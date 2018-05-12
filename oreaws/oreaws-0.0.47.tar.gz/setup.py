#!/usr/bin/env python

#from setuptools import setup
from setuptools import find_packages, setup

setup(
      name='oreaws',
      version='0.0.47',
      description='Python AWS CLI Tool',
      license='MIT',
      author='yhidetoshi',
      author_email='example@python.net',
      url='https://github.com/yhidetoshi/python-awscli-tool',
#      packages=['oreaws.oreaws'],
#      packages=['oreaws'],
      packages=find_packages(),
#      packages=find_packages(exclude=['tests']),
#      namespace_packages=['oreaws'],
#      packages=find_packages('oreaws'),
#      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      install_requires=['boto3','prettytable','click'],
      py_modules=['oreaws.modules.ec2','oreaws.modules.s3','oreaws.modules.route53','oreaws.modules.autoscaling'],
      platforms='any',
      entry_points={
              'console_scripts': [
                     'oreaws = oreaws.awscli:main',
               ],
      },
)
