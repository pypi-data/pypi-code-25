import os
from io import open
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

requires = [
    "pyyaml",
    "click",
]

setup(
    name="python-json2yaml",
    version="0.1.0",
    description="A simple command that turn json data to yaml format and vice versa. It can be used in Linux, MacOS and Window.",
    long_description=long_description,
    url="https://github.com/appstore-zencore/python-json2yaml",
    author="zencore",
    author_email="dobetter@zencore.cn",
    license="MIT",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords=['python-json2yaml'],
    requires=requires,
    install_requires=requires,
    packages=find_packages("src", exclude=["scripts"]),
    package_dir={"": "src"},
    py_modules=["python_json2yaml"],
    entry_points={
        'console_scripts': [
            "json2yaml = python_json2yaml:json2yaml",
            "yaml2json = python_json2yaml:yaml2json",
        ]
    },
    scripts=[
        "src/scripts/json2yaml.py",
        "src/scripts/yaml2json.py",
    ],
)