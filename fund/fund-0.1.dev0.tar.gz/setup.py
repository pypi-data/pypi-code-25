# coding:utf-8
from setuptools import setup, find_packages
import sys, os

version = '0.1'

def read_file(filename):
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            filename)
    if os.path.exists(filepath):
        return open(filepath).read()
    else:
        return ''

setup(name='fund',
      version=version,
      description="国内基金API接口",
      long_description=read_file('README.rst'),
      keywords='fund',
      author='fly',
      author_email='yafeile@sohu.com',
      url='https://bitbucket.org/yafeile/fund',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          "msgpack"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
