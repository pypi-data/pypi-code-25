from setuptools import setup

with open("README.rst",encoding="UTF-8") as f:
    data = f.read()

setup(name="bqLie",version="1.1.0",description="上传测试包",packages=["sub"],py_modules=["Tool",],anthor="小菜花",anthor_email="baoqian@xiaocaihua.cn",long_description=data,license="MIT")

