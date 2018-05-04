import codecs  
  
import os,sys
from setuptools import (
    setup,
)

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read() 

setup(
    name="multiJump",
    version = "0.0.5",
    author="seqyuan",
    author_email='seqyuan@gmail.com',
    url="https://github.com/seqyuan/multiJump/wiki",
    download_url = "https://codeload.github.com/seqyuan/multiJump/zip/master",
    description="multiple Jump IP do something",
    long_description=read("README.rst"),
    license="MIT",
    packages=['multiJump'],
    extras_require = {
        'sys' : [ 'sys'],
        'paramiko' : ['paramiko'],
        'socket' : ['socket'],
        'time' : ['time'],
    }
)
