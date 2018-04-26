from setuptools import setup, find_packages

setup(
    name = 'ateam',
    version = '0.0.1',
    keywords = ['ateam_test', 'egg'],
    description = 'a simple egg',
    license = 'MIT License',

    url = 'http://www.ebay.com',
    author = 'gxin',
    author_email = 'gxin@ebay.com',

    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires = [],
)
