from setuptools import setup, find_packages

VERSION = "0.1.3"

with open('README.rst') as fp:
    README = fp.read()

setup(
    name = "text2art",
    version = VERSION,
    long_description = README,
    description = "Generating controlled terminal art fonts",
    license = "MIT",
    include_package_data = True,
    author = "hangfengYang",
    author_email = "yhf5fhy@gmail.com",
    classifiers = [],
    url = "https://github.com/Fenghuapiao/text2art",
    packages = ["text2art"],
    install_requires = [
        "fire",
        "colorama",
        "pyfiglet"
    ],
    entry_points = {
        "console_scripts": [
            "text2art  =  text2art.main:main",
        ],
    }
)
