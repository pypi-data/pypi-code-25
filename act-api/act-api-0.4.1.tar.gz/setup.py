"""Setup script for the python-act library module"""

from setuptools import setup
import pypandoc

description = pypandoc.convert('README.md', 'rst')

setup(
    name="act-api",
    version="0.4.1",
    author="mnemonic AS",
    author_email="opensource@mnemonic.no",
    description="Python wrapper for act",
    #description=description,
    license="MIT",
    keywords="ACT, mnemonic",
    url="https://github.com/mnemonic-as/",
    packages=["act"],
    install_requires=['requests', 'responses'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: ISC License (ISCL)",
        ],
    )
