#from distutils.core import setup
#from setuptools import setup
from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name = 'test_vipkid_model',
    version = '0.0.1',
    keywords = ('simple', 'test'),
    description = 'just a simple test of vipkid',
    license = 'MIT',

    author = 'mingrun',
    author_email = '13271929138@163.com',

    packages = find_packages(),
    platforms = 'any',
    py_modules=['suba.aa']
)

#setup(name="test_model",version="1.0",description="vipkid's test module",author="zhaomingming",author_email="13271929138@163.com",url="www.zhaomingming.cn",py_modules=['suba.aa'])
