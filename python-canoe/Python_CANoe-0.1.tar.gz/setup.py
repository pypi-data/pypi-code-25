# -*- coding: UTF-8 -*-
#.Data:2018/5/19
from setuptools import setup, find_packages

setup(name='Python_CANoe',
      version='0.1',
      description='Control Vector CANoe API by Python',
      long_description = "Call Vector CANoe API by Python",
      keywords = ("pip", "Vector", "CAPL", "CANoe", "API", "Python"),
      url='https://github.com/hmq2018/Python-Vector-CANoe',
      author='Hz',
      author_email='weld83@126.com',
      license='MIT',
      packages=find_packages(),
      install_requires=['pywin32'],
      zip_safe=False,
      python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
      platforms='any',

      )