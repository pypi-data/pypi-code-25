#!/usr/bin/env python3
from setuptools import setup 
import yxspkg_wget
setup(name='yxspkg_wget',   
      version=yxspkg_wget.__version__,    
      description='A simple application to download images from website with a url',    
      author=yxspkg_wget.__author__,    
      install_requires=[],
      py_modules=['yxspkg_wget'],
      entry_points={
        'console_scripts': ['yxspkg_wget=yxspkg_wget:main'],},
      platforms='any',
      author_email='blacksong@yeah.net',       
      url='https://github.com/blacksong',
      classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
)   