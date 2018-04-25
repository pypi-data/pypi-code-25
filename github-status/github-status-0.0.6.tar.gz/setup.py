import re

module_file = open("github_status/__init__.py").read()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", module_file))
long_description = open('README.rst').read()

from setuptools import setup, find_packages

setup(
    name = 'github-status',
    description = 'Simple updates to SHA commits with CI the status',
    packages = find_packages(),
    author = 'Alfredo Deza',
    author_email = 'alfredo@deza.pe',
    scripts = ['bin/github-status'],
    install_requires = ['tambo>=0.4.0'],
    version = metadata['version'],
    url = 'https://github.com/alfredodeza/github-status',
    license = "MIT",
    zip_safe = False,
    keywords = "http api github ci jenkins status sha",
    long_description = long_description,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Utilities',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
    tests_require=[
        'pytest'
    ]
)
