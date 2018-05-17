# from distutils.core import setup
from setuptools import setup

def readme_file():
    with open("README.rst",encoding="utf-8") as rf:
        return rf.read()

setup(name="mytestpro"
      ,version="1.0.0"
      ,description="this a very niubi lib"
      ,packages=["mytestlib"]
      ,py_modules=["Tool"]
      ,author="----Z--"
      ,author_email="lz5215560@163.com"
      ,long_description=readme_file()
      ,url="https://www.baidu.com/"
      )
