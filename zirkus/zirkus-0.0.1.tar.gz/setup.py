from setuptools import setup

import sys
from os import path

needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(name="zirkus",
      use_scm_version=True,
      author='Holger Peters',
      description="federated blog platform",
      long_description=long_description, # Optional
      long_description_content_type='text/markdown', # Optional (see note above)
      setup_requires=['setuptools_scm'] + pytest_runner,
      tests_require=['pytest',
                     'pytest-cov',
                     'pytest-flake8',
                     'hypothesis-pytest',
                     'hypothesis'],
      packages=['zirkus'],
      classifiers=['Development Status :: 1 - Planning',
                   'Intended Audience :: Telecommunications Industry',
                   'Topic :: Communications',
                   'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
                   'Programming Language :: Python :: 3.6',
                   ])
