# from distutils.core import  setup
from setuptools import setup

def readme_file():
      with open("README.rst", encoding="utf-8") as rf:
            return rf.read()

       #功能包名称
setup(name="wxtestlib",
      #版本号
      version="1.0.0",
      #功能包的简单描述
      description="this is test lib",
      #需要将哪些包打包到目标包中
      packages=["wxlib"],
      # #涉及到的单文件模块
      py_modules=["Tool"],
      #作者
      author="wx",
      #作者联系方式
      author_email="hugh_wen@sina.com",
      #长描述
      long_description=readme_file(),
      #项目主页地址
      url="https://github.com/hugh"
      )

#打包命令python setup.py sdist