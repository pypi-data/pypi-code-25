#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: mill
# Mail: 563084506@qq.com
# Created Time:  2018-1-23 19:17:34
#############################################


from setuptools import setup, find_packages

setup(
    name = "mill_sympy_util",
    version = "0.1.0",
    keywords = ("pip", "caculate","mathtool", "mill_sympy_util", "mill"),
    description = "符号计算工具",
    long_description = "符号计算工具",
    license = "MIT Licence",

    url = "https://github.com/mill6780888/mill_sympy_util.git",
    author = "mill",
    author_email = "563084506@qq.com",

    packages = find_packages(),
    include_package_data = True,
    #platforms = "any".encode(),
    #install_requires = []
)