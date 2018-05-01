#!/usr/bin/env python

from distutils.core import setup
from pytransfer import __version__

try:
    import pytransfer
except (ImportError, SyntaxError):
    print("error: PyTransfer requires Python 3.6 or greater.")
    exit(1)

setup(
    name='PyTransfer',
    version=__version__,
    author='Patrik Janoušek',
    author_email='patrikjanousek97@gmail.com',
    description='App that simplifies usage of file hosting services (currently only https://transfer.sh)',
    long_description="I've made this app to simplify usage of file hosting services. It was primary developed for https://transfer.sh, which is scheduled to go down so this application supports simple implementation of another services in a future.",
    install_requires=['argparse', 'tqdm', 'requests'],
    packages=['pytransfer'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6'
    ],
    entry_points={
        'console_scripts': ['transfer=pytransfer.__main__:main']
    }
)
