from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='infinite_image_downloader',
    version='1.0.0',
    description='a python library for automatically downloading requested number of images from Google image search by one keyword',
    long_description=long_description, 
    long_description_content_type='text/markdown',
    url='https://github.com/zhiaozhou/infinite_image_downloader',  
    author='Zhiao Zhou', 
    author_email='zz1749@nyu.edu',  

    classifiers=[  # Optional
        # How mature is this project? Common values are
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
    ],
    keywords='google image crawl download', 
    packages=find_packages(exclude=['contrib', 'docs', 'tests']), 

    install_requires=['selenium>=3.11.0'],  
    
    scripts = [],
    entry_points = {
        'console_scripts': [
            'infinite_image_downloader = infinite_image_downloader.infinite_image_downloader:main'
        ]}
)