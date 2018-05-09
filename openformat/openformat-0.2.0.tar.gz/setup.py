from setuptools import find_packages, setup


with open('README.md') as fp:
    long_description = fp.read()


setup(
    name='openformat',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.3',
        'scipy>=0.7',
    ],
    version="0.2.0",
    author="Till Hoffmann",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
