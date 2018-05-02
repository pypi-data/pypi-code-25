try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements
from setuptools import setup, find_packages

try:
    install_reqs = parse_requirements('requirements.txt', session=False)
except:
    install_reqs = parse_requirements('nifeng_data_store.egg-info/requires.txt', session=False)

reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='nifeng-data-store',  # Required

    version='1.0.1',  # Required

    description='A simple data store project',  # Required    

    author='Nifeng',  # Optional

    author_email='tao.xu@freecoinx.com',  # Optional
    packages=find_packages(),
    install_requires=reqs
)
