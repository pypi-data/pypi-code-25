from setuptools import setup

def readme():
  with open("README.rst") as f:
    return f.read()

setup(
  name="sanjose-twitter",
  version="0.4dev",
  description="Getting trends on Twitter",
  long_description=readme(),
  author="sanjose",
  scripts=["sanjose-twitter"],
  install_requires=["twitter",]
)
