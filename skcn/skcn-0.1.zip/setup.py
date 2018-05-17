#coding:utf-8
from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'requirements.txt'),"r") as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]

setup(
    name='skcn',
    version="0.1",
    description='监控spider',
    long_description=
    '查看spider的状态',
    author="wxl",
    author_email='xiaoliangnuomi@163.com',
    url='https://github.com/Tigerwxl/nuomi',
    license='MIT',
    include_package_data=True,
    packages=find_packages(),
    install_requires=install_requires,

    entry_points={
        'console_scripts': {
            'spiderkeeper = SpiderKeeper.run:main'
        },
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
)
