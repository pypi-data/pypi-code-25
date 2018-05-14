#!/usr/bin/env python3

from setuptools import setup, find_packages
import fdump

print("all good")

setup(
    name = 'fdump',
    description = fdump.__doc__.strip(),
    url = 'https://github.com/nul-one/fdump',
    download_url = 'https://github.com/nul-one/fdump/archive/'+fdump.__version__+'.tar.gz',
    version = fdump.__version__,
    author = fdump.__author__,
    author_email = fdump.__author_email__,
    license = fdump.__licence__,
    packages = [ 'fdump' ],
    entry_points={ 
        'console_scripts': [
            'fdump=fdump.__main__:main',
        ],
    },
    install_requires = [
        #'re',
        #'sys',
        #'os',
        #'signal',
    ],
    python_requires=">=3.4.6",
)

