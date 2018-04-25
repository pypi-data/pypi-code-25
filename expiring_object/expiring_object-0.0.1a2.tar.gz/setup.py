import os

from setuptools import setup

with open(os.path.join(os.curdir, 'README.md'), 'r') as file:
    long = file.read()

setup(
    name='expiring_object',
    version='0.0.1a2',
    packages=['expiring_object'],
    url='https://github.com/sakost/expiring_object',
    license='MIT',
    author='sakost',
    author_email='sakost01+expiring_object@gmail.com',
    description='Provides making self-removal objects',
    long_description=long,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='expiring object self-removal',
    include_package_data=False,
    test_suite='tests'
)
