import os

from codecs import open

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


here = os.path.abspath(os.path.dirname(__file__))

about = {}

with open(os.path.join(here, 'pourover', '__version__.py'), 'r', 'utf-8') as ver:
    exec(ver.read(), about)

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

setup(
        name=about['__title__'],
        version=about['__version__'],
        description=about['__description__'],
        long_description=readme,
        packages=['pourover'],
        author=about['__author__'],
        author_email=about['__author_email__'],
        url='https://github.com/zthart/pourover',
        maintainer=about['__author__'],
        maintainer_email=about['__author_email__'],
        keywords='CEF parsing formatting log messages',
        platforms='any',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Topic :: System :: Logging',
            'Natural Language :: English',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy'
        ]
)