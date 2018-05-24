"""
Python Package for Back Propagation
Author: WingC
Reference: https://www.cnblogs.com/charlotte77/p/5629865.html
Date: 2018-05-18
"""

import back_propagation
from setuptools import setup

setup(
    name=back_propagation.__name__,
    version=back_propagation.__version__,
    description=back_propagation.__description__,
    author=back_propagation.__author__,
    author_email=back_propagation.__email__,
    url=back_propagation.__github__,

    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],

    keywords='Machine_Learning Back_Propagation',
    py_modules=['back_propagation'],
    install_requires=['typing'],
    extras_require={'test': ['pytest']}
)
