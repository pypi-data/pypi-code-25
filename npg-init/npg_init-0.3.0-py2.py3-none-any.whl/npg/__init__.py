from string import Template
from textwrap import dedent
import sys, os

setup_structure = dedent("""\
    # -*- coding: utf-8 -*-
    from setuptools import setup, find_packages
    try:
        long_description = open("README.rst").read()
    except IOError:
        long_description = ""
    setup(
        name={},
        version={},
        description={},
        license={},
        author={},
        packages=find_packages(),
        install_requires=[],
        long_description=long_description,
        classifiers = {}
    )
    """)


def get_information() -> dict:
    information = {}
    information["package_name"] = input("Enter your package's name: ")
    information["version"] = input("Enter first version: ")
    information["description"] = input(
        "Enter a short description about the package: ")
    information["license"] = input("Enter type of license: ")
    information["author"] = input("Enter the author's name: ")
    information["classifiers"] = [
        "Programming Language :: Python",
        "Programming Language :: Python :: {}.{}".format(sys.version_info[0],
                                                     sys.version_info[1])
    ]
    return information


def main():
    stuff = get_information()
    formatted = setup_structure.format(stuff["package_name"], stuff["version"],
                                       stuff["description"], stuff["license"],
                                       stuff["author"], stuff["classifiers"])
    os.makedirs(stuff["package_name"] + "/" + stuff["package_name"])
    os.makedirs(stuff["package_name"] + "/docs")
    os.makedirs(stuff["package_name"] + "/tests")
    with open(stuff["package_name"] + "/setup.py", "w") as file:
        file.write(formatted)
        file.close()
    open(stuff["package_name"] + "/requirements.txt", "w").close()
    open(stuff["package_name"] + "/" + stuff["package_name"] + "/__init__.py",
         "w").close()
    print("Done! Files have been made at {}".format(stuff["package_name"]))