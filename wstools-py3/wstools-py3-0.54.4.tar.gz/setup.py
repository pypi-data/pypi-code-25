#!/usr/bin/env python
import codecs
import logging
import os
import re
import subprocess
import sys
import warnings

from setuptools import setup, find_packages, Command
from setuptools.command.test import test as TestCommand

NAME = "wstools-py3"
url = "https://github.com/Synerty/wstools-py3"

# Get the version - do not use normal import because it does break coverage
base_path = os.path.dirname(__file__)
fp = open(os.path.join(base_path, 'wstools', 'version.py'))
__version__ = re.compile(r".*__version__\s*=\s*['\"](.*?)['\"]",
                         re.S).match(fp.read()).group(1)
fp.close()

# this should help getting annoying warnings from inside distutils
warnings.simplefilter('ignore', UserWarning)


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

        FORMAT = '%(levelname)-10s %(message)s'
        logging.basicConfig(format=FORMAT)
        logging.getLogger().setLevel(logging.INFO)

        # if we have pytest-cache module we enable the test failures first mode
        try:
            import pytest_cache  # noqa
            self.pytest_args.append("--ff")
        except ImportError:
            pass
        self.pytest_args.append("-s")

        if sys.stdout.isatty():
            # when run manually we enable fail fast
            self.pytest_args.append("--maxfail=1")

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # before running tests we need to run autopep8
        try:
            subprocess.check_call(
                "python -m autopep8 -r --in-place wstools/ tests/",
                shell=True)
        except subprocess.CalledProcessError:
            logging.getLogger().warn('autopep8 is not installed so '
                                     'it will not be run')
        # import here, cause outside the eggs aren't loaded
        import pytest  # noqa
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


class Release(Command):
    user_options = []

    def initialize_options(self):
        # Command.initialize_options(self)
        pass

    def finalize_options(self):
        # Command.finalize_options(self)
        pass

    def run(self):
        import json
        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib.request import urlopen
        response = urlopen(
            "http://pypi.python.org/pypi/%s/json" % NAME)
        data = json.load(codecs.getreader("utf-8")(response))
        released_version = data['info']['version']
        if released_version == __version__:
            raise RuntimeError(
                "This version was already released, remove it from PyPi if you want to release it"
                " again or increase the version number. http://pypi.python.org/pypi/%s/" % NAME)
        elif released_version > __version__:
            raise RuntimeError(
                "Cannot release a version (%s) smaller than the PyPI current release (%s)." % (
                    __version__, released_version))


class PreRelease(Command):
    user_options = []

    def initialize_options(self):
        # Command.initialize_options(self)
        pass

    def finalize_options(self):
        # Command.finalize_options(self)
        pass

    def run(self):
        import json
        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib.request import urlopen
        response = urlopen(
            "http://pypi.python.org/pypi/%s/json" % NAME)
        data = json.load(codecs.getreader("utf-8")(response))
        released_version = data['info']['version']
        if released_version >= __version__:
            raise RuntimeError(
                "Current version of the package is equal or lower than the already published ones (PyPi). Increse version to be able to pass prerelease stage.")

install_requires = [ 'six' ]

# The order of packages is significant, because pip processes them in the order
# of appearance. Changing the order has an impact on the overall integration
# process, which may cause wedges in the gate later.
tests_require = [ 'py >= 1.4', 'hacking', 'pytest', 'pytest-cov' ]

setup(
    name=NAME,
    version=__version__,
    cmdclass={'test': PyTest, 'release': Release, 'prerelease': PreRelease},
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    tests_require=tests_require,
    setup_requires=['setuptools'],
    install_requires=install_requires,
    extras_require={
        'testing': tests_require
    },
    license='BSD',
    description="WSDL parsing services package for Web Services for Python. see" + url,
    long_description=open("README.rst").read(),
    maintainer="Synerty",
    maintainer_email="contact@synerty.com",
    author='Makina Corpus',
    author_email='python@makina-corpus.com',
    provides=['wstools'],
    url=url,
    bugtrack_url='%s/issues' % url,
    home_page=url,
    keywords='api wstools wdsl web',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
