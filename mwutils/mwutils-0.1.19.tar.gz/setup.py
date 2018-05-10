from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
setup(
    name='mwutils',
    version='0.1.19',
    description='cxh ',
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://bitbucket.org/maxwin-inc/mwutils/src',  # Optional
    author='cxhjet',  # Optional
    author_email='13064576@qq.com',  # Optional
    packages=find_packages(),  # Required
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
    ],
    # install_requires=['flask>=0.11.1']
)
