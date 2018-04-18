from setuptools import setup, find_packages

setup(
    name = "mtianyan",
    version = "0.0.1",
    keywords = ("pip", "mtianyan"),
    description = "mtianyan's tool",
    long_description = "mtianyan's tool for python",
    license = "MIT Licence",

    url = "http://blog.mtianyan.cn",
    author = "mtianyan",
    author_email = "mtianyan@qq.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = []
)