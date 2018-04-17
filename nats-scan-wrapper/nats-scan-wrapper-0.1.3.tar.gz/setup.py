# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

exec(open('scanner_api/_version.py').read())
setup(
    name='nats-scan-wrapper',

    version=__version__,

    description='NATS wrapper for fast scanner development',

    long_description=long_description,

    author='Gleb Lysov',

    author_email='lysov.g.v@gmail.com',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Programming Language :: Python :: 3.5'
    ],

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=find_packages(),

    install_requires=['asyncio-nats-client']
)
