# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pipis']

package_data = \
{'': ['*']}

install_requires = \
['click>=6.7.0.0,<7.0.0.0']

entry_points = \
{'console_scripts': ['pipis = pipis:cli']}

setup_kwargs = {
    'name': 'pipis',
    'version': '0.1.0',
    'description': 'Somewhere between pip and pipsi',
    'long_description': '# PIPIS\n\n## Somewhere between pip and pipsi\n\n> "pipis" stands for "pip isolate" \\\n> and "pipi" is the french for "peepee" which is a fun name but [pipi](https://pypi.org/project/pipi/) was already taken…\n\nActually it is a rewrite of [pipsi](https://github.com/mitsuhiko/pipsi) but with [venv](https://docs.python.org/dev/library/venv.html) instead of [virtualenv](https://virtualenv.pypa.io/en/stable/).\n\n## Why ?\n\nBecause i do not care about Python 2, and `virtualenv` copies python\'s binaries while `venv` just symlink them (which i think is cleaner, but it still copies `pip` which is not clean…).\n\n## Installation\n\n```\npython3 -m venv ~/.local/venvs/pipis\nsource ~/.local/venvs/pipis/bn/activate\npip install pipis\ndeactivate\n```\n\n## Usage\n\n```\npipis --help\npipis install django\n```\n',
    'author': 'Nicolas KAROLAK',
    'author_email': 'nicolas@karolak.fr',
    'url': 'https://github.com/NicolasKAROLAK/pipi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>= 3.4.0.0, < 4.0.0.0',
}


setup(**setup_kwargs)
