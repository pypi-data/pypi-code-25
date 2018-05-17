from setuptools import setup, find_packages
from os.path import join, dirname

import helloworld

setup(
    name='stblhnv-helloworld',
    author='Stanislav Balahonov',
    author_email='stanislav.balahonov@simbirsoft.com',
    version=helloworld.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    include_package_data=True,
    install_requires=[
        'termcolor==1.1.0'
        ]
    )