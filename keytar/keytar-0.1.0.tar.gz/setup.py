"""Keytar Pip Stuff"""

from setuptools import setup

setup(
    name='keytar',
    version='0.1.0',
    description='Key Value Db Wrapper',
    author='Matt Lewis',
    author_email='domattthings@gmail.com',
    license='MIT',
    url='https://github.com/mattmatters/keytar',
    download_url='https://github.com/mattmatters/keytar/archive/0.1.0.tar.gz',
    py_modules=['keytar'],
    packages=['keytar'],
    install_requires=[
        'google',
    ],
    test_requires=[
        'pytest',
        'google',
        'boto3',
        'pymongo',
    ],
    include_package_data=True
)
