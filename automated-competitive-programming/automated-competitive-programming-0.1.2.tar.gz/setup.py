import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('acm/acm.py').read(),
    re.M
).group(1)


with open("README", "rb") as f:
    long_description = f.read().decode("utf-8")


setup(
    name="automated-competitive-programming",
    packages=["acm"],
    package_data={
        'acm': [
            'config.json'
        ]
    },
    install_requires=[
        'bs4'
    ],
    entry_points={
        "console_scripts": ['acm=acm.acm:main']
    },
    version=version,
    description="Easier competitive programming.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Dan Sclearov",
    author_email="dansclearov@gmail.com",
    # url="",
)
