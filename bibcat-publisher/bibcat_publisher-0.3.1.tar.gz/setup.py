from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name="bibcat_publisher",
    version="0.3.1",
    description="RDF Linked Data Publisher and Asset Repository",
    author="KnowledgeLinks",
    author_email="knowledgelinks.io@gmail.com",
    license="MIT",
    url="http://bibcat.org/publisher",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"],
    keywords=["rdf linked-data publisher bibframe digital repository"],
    packages=find_packages(exclude=['tests']),
    install_requires=[
        "bibcat",
        "rdfframework"
    ],
    include_package_data=True
)
