from setuptools import setup, find_packages
setup(
    name="git-semver-gen",
    version="0.1.0",
    packages=find_packages(),
    scripts=['git-semver-gen'],

    # metadata for upload to PyPI
    author="Dave Smith",
    author_email="dave.a.smith@gmail.com",
    description="And easy way to manage semantic versions for git repos with tags and a version.json file.",
    license="MIT",
    keywords="git semver",
    url="https://github.com/DiggidyDave/git-semver-gen",
)
