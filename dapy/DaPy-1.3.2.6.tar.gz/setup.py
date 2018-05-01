from setuptools import setup, find_packages
from codecs import open
from os import path
import DaPy

here = path.abspath(path.dirname(__file__))

packages = find_packages()
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
setup(
    name='DaPy',
    version=DaPy.__version__,
    description='A light data processing and analysis library for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/JacksonWuxs/DaPy',
    author='Xuansheng Wu',
    author_email='wuxsmail@163.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    keywords='data science',
    packages=packages,
##    packages=packages.extend(['data/adult/adult.csv',
##                              'data/wine/data.csv',
##                              'data/wine/info.txt',
##                              'data/iris/data.csv',
##                              'data/iris/info.txt',
##                              'data/sample.csv']),
                              
##                              
##    package_data={'adult': ['data/adult/adult.csv'],
##                  'wine': ['data/wine/data.csv',
##                           'data/wine/info.txt'],
##                  'iris': ['data/iris/data.csv',
##                           'data/iris/info.txt'],
##                  'sample': ['data/sample.csv']},
    project_urls={
        'Bug Reports': 'https://github.com/JacksonWuxs/DaPy',
        'Funding': 'https://donate.pypi.org',
        'Say Thanks!': 'https://github.com/JacksonWuxs/DaPy',
        'Source': 'https://github.com/JacksonWuxs/DaPy',
    },
)
