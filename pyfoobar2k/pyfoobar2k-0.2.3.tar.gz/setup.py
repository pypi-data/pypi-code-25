import uuid
from setuptools import setup
import os
from pip.req import parse_requirements


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
reqs_file = os.path.join(BASE_DIR, 'requirements.txt')
install_reqs = parse_requirements(reqs_file, session=uuid.uuid1())

setup(
    name="pyfoobar2k",
    version="0.2.3",
    author="Edo Ozer",
    author_email="ed0zer@gmail.com",
    description="foobar2000, foo_httpcontrol",
    license='MIT',
    keywords="pyfoobar2k, foo_httpcontrol, foobar2000",
    install_requires=["requests"],
    packages=['pyfoobar2k'],
    url="https://bitbucket.org/ed0zer/pyfoobar2k",
    long_description=read('README'),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5'
    ])
