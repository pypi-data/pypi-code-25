# Copyright (c) 2011-2018, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU General Public License version 3 (see the file LICENSE).

from setuptools import setup, find_packages
import os.path

description = open(os.path.join(
    os.path.dirname(__file__), 'README.rst'), 'rb').read().decode('UTF-8')

setup(name="lazr.postgresql",
      version="0.0.3",
      description="LAZR postgresql specific support code.",
      long_description=description,
      maintainer="Launchpad Developers",
      maintainer_email="launchpad-dev@lists.launchpad.net",
      url="https://launchpad.net/lazr-postgresql",
      packages=find_packages('src'),
      package_dir={'': 'src'},
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          ],
      install_requires=[
          'psycopg2',
          ],
      extras_require=dict(
          test=[
              'fixtures',
              'testtools',
              'van.pg',
              ]
          ),
      entry_points=dict(
        console_scripts=[
            'lp-migrate = lazr.postgresql.migrate:main',
            ]))
