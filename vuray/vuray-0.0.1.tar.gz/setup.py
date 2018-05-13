import os
import re

from setuptools import setup

package_name = 'vuray'


def get_version(package=package_name):
    with open(os.path.join(package, '__init__.py')) as init_py:
        return re.search(r'__version__ = [\'\"]([^\'\"]+)[\'\"]', init_py.read()).group(1)


def get_packages(package=package_name):
    return [dir_path for dir_path, dir_names, file_names in os.walk(package)
            if os.path.exists(os.path.join(dir_path, '__init__.py'))]


def get_description(path='README.md'):
    if not os.path.exists(path):
        return ''

    with open(path) as f:
        return f.read()


def get_requirements(path='requirements.txt'):
    if not os.path.exists(path):
        return []

    with open(path) as f:
        return f.read().splitlines()


setup(
    name=package_name,
    version=get_version(),
    url='https://github.com/vuray/vuray',
    license='UNLICENSED',
    description='VuRay checks your dependencies for known security vulnerabilities.',
    long_description=get_description(),
    author='VuRay Team',
    author_email='dev@vuray.io',
    packages=get_packages(),
    install_requires=get_requirements(),
    extras_require={
        'tests': [
            'pytest',
            'pytest-cov',
        ]
    },
    classifiers=[
        # TODO
    ],
    entry_points={
        'console_scripts': [
            'vuray=vuray.cli:run',
        ]
    },
)
