#!/usr/bin/env python3

from setuptools import setup, find_packages
import histog

setup(
    name = 'histog',
    description = histog.__doc__.strip(),
    url = 'https://github.com/nul-one/histog',
    download_url = 'https://github.com/nul-one/histog/archive/'+histog.__version__+'.tar.gz',
    version = histog.__version__,
    author = histog.__author__,
    author_email = histog.__author_email__,
    license = histog.__licence__,
    packages = [ 'histog' ],
    entry_points={ 
        'console_scripts': [
            'histog=histog.__main__:main',
        ],
    },
    install_requires = [
    ],
    python_requires=">=3.4.6",
)

