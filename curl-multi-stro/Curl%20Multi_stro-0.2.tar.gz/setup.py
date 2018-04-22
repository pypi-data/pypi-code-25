
from setuptools import setup

setup(
    author='Matthew Strozyk',
    author_email='mstrozyk25@gmail.com',
    classifiers=['Operating System :: POSIX :: Linux',
                 'Programming Language :: Python',
                 'Topic :: Utilities'],
    name='Curl Multi_stro',
    version='0.2',
    scripts=['curl_multithread.py'],
    install_requires=['requests'],
    include_package_data=True,
    
)
