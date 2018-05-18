#!/usr/bin/env python3
from setuptools import setup
from setuptools.command.build_py import build_py
from codecs import open
import subprocess
from os import path

here = path.abspath(path.dirname(__file__))


try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

class BuildECA(build_py):
    def run(self):
        command = "mkdir deps/"
        process = subprocess.Popen(command, shell=True)
        process.wait()

        command = "git clone https://github.com/jmejia8/eca"
        process = subprocess.Popen(command, shell=True, cwd="deps")
        process.wait()

        command = "make && mv eca.so ../../ecapy/eca.so"
        process = subprocess.Popen(command, shell=True, cwd="deps/eca")
        process.wait()
        
        build_py.run(self)

setup(
    name='ecapy',
    description='Evolutionary Centers Algorithm: Module for Python coded in C',
    url='https://github.com/jmejia8/ecapy',
    version='1.0.1',
    license='MIT',

    long_description=long_description,

    author='Jesus Mejia',
    author_email='jesusmejded@gmail.com',

    classifiers=[  
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='optimization evolutionary metaheuristic',

    packages=['ecapy'],

    dependency_links=['https://github.com/jmejia8/eca/archive/master.zip'],
    
    extras_require={  
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

    cmdclass={'build_py': BuildECA},
    include_package_data=True,


    project_urls={  
        'Bug Reports': 'https://github.com/jmejia8/ecapy/issues',
        'Source': 'https://github.com/jmejia8/ecapy/',
    },

    # Test configuration
    setup_requires=[
        'pytest-runner',
    ],

     tests_require=[
        'pytest'
    ],
)
