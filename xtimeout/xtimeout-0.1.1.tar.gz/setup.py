from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

with open('README.rst', encoding='utf8') as f:
    long_description = f.read()

setup(
    name='xtimeout',
    version='0.1.1',
    description='Trace a timeout function call and handle with it',
    long_description=long_description,
    author='amos402',
    author_email='amos_402@msn.com',
    url='https://github.com/amos402/py-xtimeout',
    keywords=['timeout', 'inject', 'timeout handler', 'function timetout'],
    license='MIT',
    packages=['tests'],
    package_dir={'': 'src', 'tests': 'tests'},
    py_modules=['xtimeout'],
    ext_modules=[
        Extension('_xtimeout', ['src/_xtimeout.cpp'])
    ],
    test_suite='tests',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: C++',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python',
    ]
)