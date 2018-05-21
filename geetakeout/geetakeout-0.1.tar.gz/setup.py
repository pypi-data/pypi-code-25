import subprocess
import os
import sys
import setuptools
from setuptools import find_packages
from setuptools.command.test import test as TestCommand
from distutils.version import StrictVersion
from setuptools import __version__ as setuptools_version

if StrictVersion(setuptools_version) < StrictVersion('38.3.0'):
    raise SystemExit(
        'Your `setuptools` version is old. '
        'Please upgrade setuptools by running `pip install -U setuptools` '
        'and try again.'
    )

try:
    subprocess.call(["git"])
except OSError as e:
    if e.errno==os.errno.ENOENT:
        raise SystemExit(
            'Git not found Install Git '
            'and try again.'
        )
    else:
        sys.exit("Git not found Install Git "+str(e))
def readme():
    with open('README.md') as f:
        return f.read()
setuptools.setup(
    name='geetakeout',
    version='0.1',
    packages=find_packages(),
    package_data={'geetakeout': ['geckodriver','geckodriver.exe']},
    url='https://github.com/samapriya/gee-takeout',
    install_requires=['google-api-python-client >= 1.5.4','earthengine_api ==0.1.134','requests >= 2.18.4','clipboard>=0.0.4','beautifulsoup4 >= 4.6.0',
                      'pytest >= 3.0.0','selenium >=3.9.0','python_dateutil >=2.6.1','pySmartDL==1.2.5','lxml>=4.1.1','pathlib>=1.0.1'],
    license='Apache 2.0',
    long_description=open('README.txt').read(),
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Scientific/Engineering :: GIS',
    ),
    author='Samapriya Roy',
    author_email='samapriya.roy@gmail.com',
    description='Google Earth Engine Takeout Tool',
    entry_points={
        'console_scripts': [
            'geetakeout=geetakeout.geetakeout:main',
        ],
    },
)
