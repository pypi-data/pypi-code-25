# setuptools 不会产生source code 的package，有时会安装到公目录
# from setuptools import setup
from distutils.core import setup

setup(
    name='mwpermission',
    version='0.1.17',
    description='maxwin permission ',
    packages=['mwpermission'],
    package_data={
        '': ['*.*']
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'flask>=0.11.1'
    ]
)
