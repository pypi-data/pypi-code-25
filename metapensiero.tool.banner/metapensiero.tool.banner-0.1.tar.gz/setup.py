# -*- coding: utf-8 -*-
# :Project:   metapensiero.tool.banner -- Minimalistic SysV banner tool
# :Created:   Thu 25 Jan 2018 23:15:19 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Lele Gaifax
#

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst'), encoding='utf-8') as f:
    CHANGES = f.read()
with open(os.path.join(here, 'version.txt'), encoding='utf-8') as f:
    VERSION = f.read().strip()

setup(
    name="metapensiero.tool.banner",
    version=VERSION,
    url="https://gitlab.com/metapensiero/metapensiero.tool.banner.git",

    description="Minimalistic SysV banner tool",
    long_description=README + '\n\n' + CHANGES,

    author="Lele Gaifax",
    author_email="lele@metapensiero.it",

    license="GPLv3+",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        ],
    keywords="",

    packages=['metapensiero.tool.' + package
              for package in find_packages('src/metapensiero/tool')],
    package_dir={'': 'src'},
    namespace_packages=['metapensiero', 'metapensiero.tool'],

    install_requires=['setuptools'],
    extras_require={
        'dev': [
            'metapensiero.tool.bump_version',
            'readme_renderer',
        ]
    },

    entry_points="""\
    [console_scripts]
    banner = metapensiero.tool.banner:main
    """,
)
