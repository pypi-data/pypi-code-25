#!/usr/bin/env python

"""
setup.py file for SWIG example
"""

from distutils.core import setup, Extension
# from setuptools import setup, Extension

md5distro_module = Extension('_md5distro',
                           sources=['md5distrov1_wrap.c', 'md5v1.c'],
                           )

setup (name = 'md5distro',
       version = '0.48',
       author = "Dan Siewers",
       author_email = "kokovec69@gmail.com",
       description = """MD5 Hasher For Distributed (Serverless) Hashes""",
       ext_modules = [md5distro_module],
       py_modules = ["md5distro"],
       )
