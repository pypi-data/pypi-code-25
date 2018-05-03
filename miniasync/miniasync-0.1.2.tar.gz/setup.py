import os
import sys

from setuptools import setup

MIN_PYTHON = (3, 5)
MIN_PYTHON_REQ = '>=%s' % '.'.join(str(i) for i in MIN_PYTHON)

if sys.version_info[:2] < MIN_PYTHON:
    raise Exception("miniasync requires Python %s." % MIN_PYTHON_REQ)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='miniasync',
    version='0.1.2',
    description='miniasync is a small library build on top of asyncio to faciliate running small portions of asynchronous code in an otherwise synchronous application',
    long_description=read('README.rst') + '\n\n' + read('CHANGES.rst'),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)"
    ],
    author='Alice Heaton',
    license='LGPLv3+',
    url='https://gitlab.com/alich75/miniasync',
    keywords='asyncio',
    packages=['miniasync'],
    install_requires=[],
    python_requires=MIN_PYTHON_REQ,
)
