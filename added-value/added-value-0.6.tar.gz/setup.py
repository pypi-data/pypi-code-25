# -*- coding: utf-8 -*-
import os
import io

from setuptools import setup


with open('README.rst', 'r') as readme:
    long_description = readme.read()

requires = ['Sphinx>=1.7.4']


def local_file(*name):
    return os.path.join(
        os.path.dirname(__file__),
        *name)


def read(name, **kwargs):
    with io.open(
        name,
        encoding=kwargs.get("encoding", "utf8")
    ) as handle:
        return handle.read()


def read_version():
    "Read the `(version-string, version-info)` from `added_value/version.py`."
    version_file = local_file('added_value', 'version.py')
    local_vars = {}
    with open(version_file) as handle:
        exec(handle.read(), {}, local_vars)  # pylint: disable=exec-used
    return (local_vars['__version__'], local_vars['__version_info__'])

install_requires = [
    'sphinx'
]


setup(
    name='added-value',
    packages=['added_value'],
    version = read_version()[0],
    url='https://github.com/sixty-north/added-value',
    download_url="https://pypi.python.org/pypi/added-value",
    license='BSD',
    author='Robert Smallshire',
    author_email='rob@sixty-north.com',
    description='Sphinx "added-value" extension',
    long_description=long_description,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    include_package_data=True,
    install_requires=install_requires,
    requires=['sphinx'],
    extras_require={
        'test': ['pytest', 'sphinx-testing'],
        'docs': ['sphinx', 'sphinx_rtd_theme'],
    }
)
