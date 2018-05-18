# coding=GBK
'''
Created on 2018年5月18日

@author: HZH
'''
from setuptools import setup, find_packages

setup(
    name="hzh_nester_0518",
    packages=find_packages(),
    version='0.9.3',
    description="command line tool for auto tuner",
    author="hzh",
    author_email='zhiheng_hu@yeah.net',
    url="https://github.com/username/reponame",
    download_url='https://github.com/username/reponame/archive/0.1.tar.gz',
    keywords=['command', 'line', 'tool'],
    classifiers=[],
    entry_points={
        'console_scripts': [
        'command1 = advisorhelper.cmdline:execute'
        'command2 = adviserserver.create_algorithm:run',
        'command3 = adviserserver.run_algorithm:run'
    ]
    },
    install_requires=[
        'grpcio>=1.7.0',
        'numpy',
        'requests',
    ]
)