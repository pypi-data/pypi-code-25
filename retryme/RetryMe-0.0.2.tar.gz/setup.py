from setuptools import setup
from setuptools import setup, find_packages, __version__ as setuptools_version
import RetryMe

version = RetryMe.__version__
url = "https://github.com/xulei890817/retryme"


def readme():
    with open("README.rst", "r") as infile:
        return infile.read()


setup(
    name='RetryMe',
    version=version,
    packages=['RetryMe'],
    url=url,
    license='',
    author='leixu',
    author_email='lei.xu@grandhonor.net',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.5',
    install_requires=[

    ],
    description='An easy way to retry your code.'
)
