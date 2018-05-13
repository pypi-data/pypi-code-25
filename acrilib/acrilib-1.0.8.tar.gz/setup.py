import sys
from setuptools import setup
import importlib.util
import os


'''
is the Python package in your project. It's the top-level folder containing the
__init__.py module that should be in the same directory as your setup.py file
/-
  |-- README.rst
  |-- CHANGES
  |-- AUTHORS
  |-- LICENSE
  |-- setup.py
  |-- <package-name>
  |  |-- __init__.py
  |  |-- <some-program>.py
  |  |-- bin
  |  |   |-- <some executables (.py or others)>
  |  |-- <internal package folders>
  |  |   |-- <some-program.py>

To create package and upload:

  python setup.py register (only once when first time loading Python)
  python setup.py sdist
  twine upload -s dist/path/to/gz

'''


def import_setup_utils():
    # load setup utils
    try:
        setup_utils_spec = \
            importlib.util.spec_from_file_location("setup.utils",
                                                   "setup_utils.py")
        setup_utils = importlib.util.module_from_spec(setup_utils_spec)
        #print(setup_utils)
        setup_utils_spec.loader.exec_module(setup_utils)
    except Exception as err:
        raise RuntimeError("Failed to find setup_utils.py."
                           " Please copy or link.") from err
    return setup_utils


# setup_utils = import_setup_utils()
sys.path.append(os.path.dirname(__file__))
import setup_utils 
PACKAGE = "acrilib"
NAME = PACKAGE
DESCRIPTION = ('acrilib is a python library of programming patterns'
               ' commonly used in Python')
metahost = setup_utils.metahost(PACKAGE)
AUTHORS, AUTHOR_EMAILS = setup_utils.read_authors(metahost=metahost)
URL = 'https://github.com/Acrisel/acrilib'
VERSION = setup_utils.read_version(metahost=metahost)

# Find previous installation and warn. See #18115.
existing_path = None
if "install" in sys.argv:
    existing_path = setup_utils.existing_package(PACKAGE)

scripts = setup_utils.scripts(PACKAGE)

# Find all sub packages
packages = setup_utils.packages(PACKAGE)

setup_info = {
    'name': NAME,
    'version': VERSION,
    'url': URL,
    'author': AUTHORS,
    'author_email': AUTHOR_EMAILS,
    'description': DESCRIPTION,
    'long_description': open("README.rst", "r").read(),
    'license': 'MIT',
    'keywords': ('library sequence logger yield singleton thread synchronize'
                 ' resource pool utilities os ssh xml excel mail'),
    'packages': packages,
    'scripts': scripts,
    'install_requires': [],
    'extras_require': {'dev': [], 'test': []},
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        # 'Framework :: Project Settings and Operation',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Application '
        'Frameworks',
        'Topic :: Software Development :: Libraries :: Python '
        'Modules']}

from pprint import pprint
#pprint(setup_info)
setup(**setup_info)


if existing_path:
    sys.stderr.write("""

========
WARNING!
========

You have just installed %(name)s over top of an existing
installation, without removing it first. Because of this,
your install may now include extraneous files from a
previous version that have since been removed from
Accord. This is known to cause a variety of problems. You
should manually remove the

%(existing_path)s

directory and re-install %(name)s.

""" % {"existing_path": existing_path,
       "name": NAME, })
