#!/usr/bin/env python3'
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name             = 'todolist',
    version          = '0.1.7',
    description      = 'The Open Source CLI To Do List App',
    long_description = long_description,
    long_description_content_type ="text/markdown",
    author           = 'Kang MinSeok',
    author_email     = 'stillnessfate@gmail.com',
    url              = 'https://github.com/StillnessFate/Open-Source-ToDo-List',
    download_url     = 'https://github.com/StillnessFate/Open-Source-ToDo-List/archive/master.tar.gz',
    install_requires = [ ],
    packages         = find_packages(exclude = ["test.py", "test_code.py"]),
    keywords         = ['todo list', 'task manager'],
    python_requires  = '>=3',
    package_data     =  {'todolist' : [ "LICENSE" ]},
    zip_safe=False,
    classifiers      = [
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    entry_points={
        'console_scripts': [
            'todolist = todolist.__main__:main'
        ]
    }
)