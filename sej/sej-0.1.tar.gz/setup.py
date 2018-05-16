from setuptools import setup, find_packages

setup(
    name = "sej",
    version = "0.1",
    keywords = "pip, Chinese, segmentation, HMM",
    description = "Chinese Segmentation Tool",
    long_description = "Chinese Segmentation Tool, using HMM",
    license = "MIT Licence",

    author = "begosu",
    author_email = "cocaer.cl@gmail.com",

    packages = ['sej'],
    package_dir = {'sej':'sej'},
    include_package_data = True,
    platforms = "any",
    install_requires = ['pytrie']
)