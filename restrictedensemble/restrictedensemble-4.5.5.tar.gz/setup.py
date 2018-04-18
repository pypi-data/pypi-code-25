#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: LiangjunFeng
# Mail: zhumavip@163.com
# Created Time:  2018-4-16 19:17:34
#############################################

from setuptools import setup, find_packages

setup(
    name = "restrictedensemble",
    version = "4.5.5",
    keywords = ("pip", "Classifier","EnsembleLearning", "RestrctedBoosting", "Tree"),
    description = "A Boosting Frame for Classifier",
    long_description = "A Boosting Frame for Classifier，Currently only CART tree and SVC are provided as base classifiers",
    license = "MIT Licence",

    url = "https://github.com/LiangjunFeng/restrictedemsemble",
    author = "LiangjunFeng",
    author_email = "zhumavip@163.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["pandas","numpy","sklearn"]
)
