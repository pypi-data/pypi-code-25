import re

module_file = open("remoto/__init__.py").read()
metadata = dict(re.findall(r"__([a-z]+)__\s*=\s*['\"]([^'\"]*)['\"]", module_file))
long_description = open('README.rst').read()
install_requires = []

from setuptools import setup, find_packages


setup(
    name = 'psukys-remoto',
    description = 'Execute remote commands or processes. Fork with changes to allow continuous output for remote functions',
    packages = find_packages(),
    author = 'Alfredo Deza, Paulius Sukys',
    author_email = 'contact@deza.pe, paul.sukys@gmail.com',
    version = metadata['version'],
    url = 'http://github.com/psukys/remoto',
    license = "MIT",
    zip_safe = False,
    keywords = "remote, commands, unix, ssh, socket, execute, terminal",
    install_requires=[
        'execnet',
    ] + install_requires,
    long_description = long_description,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ]
)
