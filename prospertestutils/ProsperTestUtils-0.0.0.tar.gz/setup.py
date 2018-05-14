"""wheel setup for Prosper common utilities"""
from codecs import open
import importlib

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


def get_version(*args):
    """find __version__ for making package

    Args:
        (str): python path to project

    Returns:
        str: __version__ value

    """

    module = '.'.join(args) + '._version'
    package = importlib.import_module(module)

    version = package.__version__

    return version

def get_library_name(*args):
    """find __library_name__ for making package

    TODO:
        Fix in 3.7: https://stackoverflow.com/a/48916205
    Args:
        (str): python path to project

    Returns:
        str: __library_name__ value

    """

    module = '.'.join(args) + '._version'
    package = importlib.import_module(module)

    library_name = package.__library_name__

    return library_name

def hack_find_packages(include_str):
    """patches setuptools.find_packages issue

    setuptools.find_packages(path='') doesn't work as intended

    Returns:
        list: append <include_str>. onto every element of setuptools.find_pacakges() call

    """
    new_list = [include_str]
    for element in find_packages(include_str):
        new_list.append(include_str + '.' + element)

    return new_list

__package_name__ = 'ProsperTestUtils'
__library_name__ = 'test_utils'


class PyTest(TestCommand):
    """PyTest cmdclass hook for test-at-buildtime functionality

    http://doc.pytest.org/en/latest/goodpractices.html#manual-integration

    """
    user_options = [
        ('pytest-args=', 'a', 'Arguments to pass to pytest')

    ]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = [
            'tests',
            '-rx',
            '-v',
            '--log-level=DEBUG',
            '--cov=prosper/' + __library_name__,
            '--cov-report=term-missing',
            '--cov-config=.coveragerc',
        ]

    def run_tests(self):
        import shlex
        import pytest
        pytest_commands = []
        try:
            pytest_commands = shlex.split(self.pytest_args)
        except AttributeError:
            pytest_commands = self.pytest_args
        errno = pytest.main(pytest_commands)
        exit(errno)

class QuickTest(PyTest):
    """wrapper for quick-testing for devs"""
    user_options = [('pytest-args=', 'a', 'Arguments to pass to pytest')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = [
            'tests',
            '-rx',
            '-n',
            '4',
            '--log-level=DEBUG',
            '--cov=prosper/' + __library_name__,
            '--cov-report=term-missing',
            '--cov-config=.coveragerc',
        ]


with open('README.rst', 'r', 'utf-8') as fh:
    README = fh.read()

setup(
    name=__package_name__,
    description='Test helpers for Prosper projects',
    version=get_version('prosper', __library_name__),
    long_description=README,
    author='John Purcell',
    author_email='prospermarketshow@gmail.com',
    url='https://github.com/EVEprosper/' + __package_name__,
    license='Unlicense',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'License :: Public Domain',
    ],
    keywords='testing docker configuration-management pytest',
    packages=hack_find_packages('prosper'),
    include_package_data=True,
    package_data={
        '': ['LICENSE', 'README.rst', ],
        'prosper': [
            'test_utils/root_schema.schema',
            'test_utils/version.txt',
            'test_utils/app.cfg',
        ],
    },
    entry_points={
        'console_scripts': [
            'update-prosper-schemas=prosper.test_utils.schema_utils:run_plumbum',
        ]
    },
    python_requires='>=3.5',
    install_requires=[
        'prospercommon',
        'requests',
        'semantic_version',
        'plumbum',
        'docker',
        'deepdiff',
        'jsonschema',
        'genson',
        'pymongo',
        'dnspython',
    ],
    tests_require=[
        'pytest',
        'pytest_cov',
        'pytest-xdist',
        'tinymongo',
    ],
    extras_require={
        'dev':[
            'sphinx',
            'sphinxcontrib-napoleon',
        ],
    },
    cmdclass={
        'test': PyTest,
        'fast': QuickTest,
    },
)
