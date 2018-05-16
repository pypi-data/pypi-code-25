import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='concierge_theme_gc',
    version='0.2',
    packages=find_packages(),
    include_package_data=True,
    license='OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)',
    description='The Government of Canada theme for Concierge',
    url='https://github.com/Pleio/concierge-theme-gc',
    maintainer='GCTools Team',
    maintainer_email='mark.wooff@tbs-sct.gc.ca',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)