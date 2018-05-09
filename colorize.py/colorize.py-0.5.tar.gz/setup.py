from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
  name="colorize.py",
  version='0.5',
  scripts=['colorize.py'],
  install_requires=['docopt>=0.2'],
  author="Henry Qin",
  author_email="root@hq6.me",
  description="Add colors to plain text lines matching either a Python string or regular expression",
  long_description=long_description,
  platforms=["Any Platform supporting ANSI escape codes"],
  license="MIT",
  url="https://github.com/hq6/Colorize"
)
