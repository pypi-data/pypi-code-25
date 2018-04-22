from setuptools import setup, find_packages
from os.path import join, isfile
from os import walk

def package_files(directories):
    paths = []
    for item in directories:
        if isfile(item):
            paths.append(join('..', item))
            continue
        for (path, directories, filenames) in walk(item):
            for filename in filenames:
                paths.append(join('..', path, filename))
    return paths

setup(
    name = "mtianyan",
    version = "0.0.8",
    keywords = ("pip", "mtianyan"),
    description = "mtianyan's tool",
    long_description = "mtianyan's tool",
    license = "MIT Licence",

    url = "http://blog.mtianyan.cn",
    author = "mtianyan",
    author_email = "mtianyan@qq.com",

    packages = find_packages(),
        package_data={
        '': package_files([
            'mtianyan/plugins/',
            'mtianyan/download_helper/'
        ])
    },
    platforms = "any",
    install_requires = ["beautifulsoup4", "requests"]
)
