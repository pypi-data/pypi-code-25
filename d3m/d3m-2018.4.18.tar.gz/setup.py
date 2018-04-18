import os
import sys
from setuptools import setup, find_packages

PACKAGE_NAME = 'd3m'
MINIMUM_PYTHON_VERSION = 3, 6


def check_python_version():
    """Exit when the Python version is too low."""
    if sys.version_info < MINIMUM_PYTHON_VERSION:
        sys.exit("Python {}.{}+ is required.".format(*MINIMUM_PYTHON_VERSION))


def read_package_variable(key):
    """Read the value of a variable from the package without importing."""
    module_path = os.path.join(PACKAGE_NAME, '__init__.py')
    with open(module_path) as module:
        for line in module:
            parts = line.strip().split(' ')
            if parts and parts[0] == key:
                return parts[-1].strip("'")
    assert False, "'{0}' not found in '{1}'".format(key, module_path)


check_python_version()
version = read_package_variable('__version__')

setup(
    name=PACKAGE_NAME,
    version=version,
    description='Common code for D3M project',
    author='DARPA D3M Program',
    packages=find_packages(exclude=['contrib', 'docs', 'site', 'tests*']),
    package_data={'d3m': ['metadata/schemas/*/*.json']},
    install_requires=[
        'scikit-learn[alldeps]==0.19.1',
        'pytypes==1.0b3.post40',
        'frozendict==1.2',
        'numpy==1.14.2',
        'jsonschema==2.6.0',
        'requests==2.18.4',
        'strict-rfc3339==0.7',
        'rfc3987==1.3.7',
        'webcolors==1.8.1',
        'dateparser==0.7.0',
        'pandas==0.22.0',
        'networkx==2.1',
        'typing-inspect==0.2.0',
        'GitPython==2.1.9',
        'jsonpath-ng==1.4.3',
        'custom-inherit==2.2.0',
        'PyYAML==3.12',
    ],
    # For now an extra.
    # See: https://gitlab.com/datadrivendiscovery/d3m/issues/66
    extras_require={
        'arrow': [
            'pyarrow==0.9.0',
        ],
    },
    tests_require=[
        'docker[tls]==2.7',
    ],
    dependency_links=[
        'git+https://github.com/Stewori/pytypes.git@8693de189d5f6bbb9c4401fa5ca04dd20e9cc485#egg=pytypes-1.0b3.post40',
    ],
    url='https://gitlab.com/datadrivendiscovery/d3m',
)
