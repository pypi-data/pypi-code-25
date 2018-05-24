from setuptools import setup, find_packages

setup(name='isaExplorer',
    version='0.1.0',
    description='Explore and manipulate the contents of ISATAB files',
    url='http://github.com/phenomecentre/isaexplorer',
    author='Noureddin Sadawi',
    author_email='n.sadawi@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'isatools>=0.9.0'
    ],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    long_description = """\
        Module for querying ISATAB study design files
        ---------------------------------------------

        .. image:: https://travis-ci.org/phenomecentre/isaExplorer.svg?branch=master
        :target: https://travis-ci.org/phenomecentre/isaExplorer
        :alt: Travis CI build status

        .. image:: https://codecov.io/gh/phenomecentre/isaExplorer/branch/master/graph/badge.svg
        :target: https://codecov.io/gh/phenomecentre/isaExplorer
        :alt: Test coverage

        |

        Tools for querying `ISA-TAB <http://isa-tools.org>`_ study description files.

        """,
    zip_safe=True
    )
