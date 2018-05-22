from setuptools import setup, find_packages
import re
import sys


VERSIONFILE="opedia_dataset_validator/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

url = 'https://github.com/ctberthiaume/opedia_dataset_validator'
download_url = url + '/archive/{}.tar.gz'.format(verstr)


setup(
    name='opedia_dataset_validator',
    version=verstr,
    author='Chris T. Berthiaume',
    author_email='chrisbee@uw.edu',
    license='LICENSE.txt',
    description='A tool to validate Opedia dataset files.',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    url=url,
    download_url=download_url,
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ],
    keywords = ['opedia', 'validator'],
    python_requires='>=2.6, <4',
    install_requires=[
        'arrow',
        'click',
        'oyaml',
        'pandas',
        'xlrd'
    ],
    entry_points={
        'console_scripts': [
            'opedia_dataset_validator = opedia_dataset_validator.cli:main'
        ]
    }
)
