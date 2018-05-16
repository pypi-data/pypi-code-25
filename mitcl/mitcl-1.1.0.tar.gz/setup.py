"""
set up tools for mitcl
"""
from setuptools import setup, find_packages
from codecs import open
from os import path
import os


here = path.abspath(path.dirname(__file__))

def save_datas():
    data_path = os.path.join(os.getenv('HOME'), '.mitcl')
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    return data_path

data_path = save_datas()

setup(
    #
    include_package_data=True,
    name='mitcl',
    version='1.1.0',
    description='MIT OCW check and download',
    license='MIT',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        'Topic :: Software Development :: Build Tools',
    	'Programming Language :: Python :: 2',
    	'Programming Language :: Python :: 2.7',
    	'Programming Language :: Python :: 3',
    	'Programming Language :: Python :: 3.2',
    	'Programming Language :: Python :: 3.3',
    	'Programming Language :: Python :: 3.4',
        ],
    packages=find_packages(),
    data_files=[(data_path, ['mitcl/data/mitcl.dat'])],
    zip_safe=False,
    entry_points={
        'console_scripts':[
            'mitcl=mitcl.mitcl:main',
            ],
        }
    )
