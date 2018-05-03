import os

try:
    from pip._internal.req import parse_requirements
except ImportError:
    from pip.req import parse_requirements
from setuptools import setup, find_packages

install_reqs = parse_requirements('requirements.txt', session=False)

reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='magicstore',

    version=f'1.0.{os.environ["BUILD_VERSION"]}',

    description='A simple data store project',

    author='Nifeng',

    author_email='tao.xu@freecoinx.com',
    packages=find_packages(),
    install_requires=reqs
)
